from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import date
import json
import re


@dataclass
class Experience:
    company: str
    title: str
    start: Optional[str] = None  # YYYY-MM or free text
    end: Optional[str] = None    # YYYY-MM or "Present"
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Education:
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Resume:
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    experiences: List[Experience] = field(default_factory=list)
    educations: List[Education] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)  # место для произвольных полей

    # --- CRUD для навыков ---
    def add_skill(self, skill: str) -> None:
        s = skill.strip()
        if s and s.lower() not in (x.lower() for x in self.skills):
            self.skills.append(s)

    def remove_skill(self, skill: str) -> bool:
        lowered = skill.strip().lower()
        for i, s in enumerate(self.skills):
            if s.lower() == lowered:
                del self.skills[i]
                return True
        return False

    # --- CRUD для опыта и образования ---
    def add_experience(self, company: str, title: str, start: Optional[str] = None,
                       end: Optional[str] = None, description: Optional[str] = None) -> None:
        self.experiences.append(Experience(company=company, title=title, start=start, end=end, description=description))

    def add_education(self, institution: str, degree: Optional[str] = None, field: Optional[str] = None,
                      start: Optional[str] = None, end: Optional[str] = None, description: Optional[str] = None) -> None:
        self.educations.append(Education(institution=institution, degree=degree, field=field, start=start, end=end, description=description))

    # --- Сериализация / десериализация ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "summary": self.summary,
            "skills": list(self.skills),
            "experiences": [e.to_dict() for e in self.experiences],
            "educations": [ed.to_dict() for ed in self.educations],
            "extra": dict(self.extra)
        }

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Resume":
        r = cls(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            summary=data.get("summary"),
            skills=list(data.get("skills", [])),
            extra=dict(data.get("extra", {}))
        )
        for ex in data.get("experiences", []):
            r.experiences.append(Experience(**ex))
        for ed in data.get("educations", []):
            r.educations.append(Education(**ed))
        return r

    @classmethod
    def from_json(cls, s: str) -> "Resume":
        data = json.loads(s)
        return cls.from_dict(data)

    # --- Полезные представления ---
    def render_text(self) -> str:
        lines = []
        lines.append(f"{self.first_name} {self.last_name}")
        if self.email:
            lines.append(f"Email: {self.email}")
        if self.phone:
            lines.append(f"Phone: {self.phone}")
        if self.summary:
            lines.append("\nSummary:")
            lines.append(self.summary)
        if self.skills:
            lines.append("\nSkills:")
            lines.append(", ".join(self.skills))
        if self.experiences:
            lines.append("\nExperience:")
            for e in self.experiences:
                lines.append(f"- {e.title} @ {e.company} ({e.start or ''} - {e.end or ''})")
                if e.description:
                    lines.append(f"  {e.description}")
        if self.educations:
            lines.append("\nEducation:")
            for ed in self.educations:
                deg = f"{ed.degree + ', ' if ed.degree else ''}{ed.field or ''}".strip(", ")
                lines.append(f"- {ed.institution} {(' — ' + deg) if deg else ''} ({ed.start or ''} - {ed.end or ''})")
                if ed.description:
                    lines.append(f"  {ed.description}")
        return "\n".join(lines)

    def render_markdown(self) -> str:
        md = []
        md.append(f"# {self.first_name} {self.last_name}")
        if self.email or self.phone:
            contact = " • ".join(filter(None, [self.email, self.phone]))
            md.append(contact)
        if self.summary:
            md.append("## Summary")
            md.append(self.summary)
        if self.skills:
            md.append("## Skills")
            md.append(", ".join(self.skills))
        if self.experiences:
            md.append("## Experience")
            for e in self.experiences:
                md.append(f"**{e.title}**, *{e.company}* — {e.start or ''} — {e.end or ''}")
                if e.description:
                    md.append(f"> {e.description}")
        if self.educations:
            md.append("## Education")
            for ed in self.educations:
                md.append(f"**{ed.institution}** {('— ' + (ed.degree or '')) if ed.degree else ''} {ed.start or ''} — {ed.end or ''}")
                if ed.description:
                    md.append(f"> {ed.description}")
        return "\n\n".join(md)

    # --- Валидация простая ---
    def validate(self) -> Dict[str, Any]:
        problems = []
        if not self.first_name or not self.last_name:
            problems.append("missing_name")
        if self.email:
            # простая проверка email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
                problems.append("invalid_email")
        if self.phone:
            if len(re.sub(r"\D", "", self.phone)) < 7:
                problems.append("invalid_phone")
        return {"ok": len(problems) == 0, "problems": problems}

    # --- Простой скоринг совпадения с JD (вакансией) по навыкам и тексту ---
    def match_score(self, job_description: str) -> float:
        """
        Возвращает число от 0.0 до 1.0 — простая мера совпадения.
        Метод учитывает:
         - долю навыков, найденных в JD
         - пересечение ключевых слов между summary+experience и JD
        (это базовый эвристический скор — можно заменить на TF-IDF / BERT позже)
        """
        jd = job_description.lower()
        # skills match
        if self.skills:
            matched = sum(1 for s in self.skills if re.search(r'\b' + re.escape(s.lower()) + r'\b', jd))
            skill_score = matched / len(self.skills)
        else:
            skill_score = 0.0

        # keyword overlap from summary + experiences
        text_parts = " ".join(filter(None, [self.summary or ""] + [e.description or "" for e in self.experiences]))
        words = set(re.findall(r"\w+", text_parts.lower()))
        jd_words = set(re.findall(r"\w+", jd))
        if words:
            overlap = words & jd_words
            keyword_score = len(overlap) / max(1, len(words))
        else:
            keyword_score = 0.0

        # weight: skills 0.7, keywords 0.3
        score = 0.7 * skill_score + 0.3 * keyword_score
        return max(0.0, min(1.0, score))

    # --- Анонимизация (удаляет персональные контактные данные) ---
    def anonymize(self) -> "Resume":
        r = Resume.from_dict(self.to_dict())
        r.first_name = ""
        r.last_name = ""
        r.email = None
        r.phone = None
        # можно также убрать institutions/companies по желанию
        return r
