import os


class Skill:
    def __init__(self, name, path, description=""):
        self.name = name
        self.path = path
        self.description = description
        self.content = ""

    def load(self):
        skill_md = os.path.join(self.path, "SKILL.md")
        if os.path.exists(skill_md):
            with open(skill_md, "r", encoding="utf-8") as f:
                self.content = f.read()
        return self.content


class SkillManager:
    def __init__(self, skills_dir="skills"):
        self.skills_dir = skills_dir
        self._skills = {}

    def scan(self):
        self._skills = {}
        if not os.path.isdir(self.skills_dir):
            return self._skills

        for name in sorted(os.listdir(self.skills_dir)):
            skill_path = os.path.join(self.skills_dir, name)
            skill_md = os.path.join(skill_path, "SKILL.md")
            if os.path.isdir(skill_path) and os.path.exists(skill_md):
                skill = Skill(name=name, path=skill_path)
                skill.load()
                # 取第一行非标题行作为描述
                for line in skill.content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        skill.description = line[:80]
                        break
                self._skills[name] = skill

        return self._skills

    def list_all(self):
        return list(self._skills.values())

    def get(self, name):
        return self._skills.get(name)

    def build_context(self, skill_name):
        """返回 skill 的 system prompt 片段。"""
        skill = self.get(skill_name)
        if skill is None:
            return ""
        return (
            f"[skill: {skill.name}]\n"
            f"{skill.content}\n"
            f"[/skill: {skill.name}]"
        )
