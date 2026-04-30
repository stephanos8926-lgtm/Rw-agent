import os
import yaml

class SkillsLoader:
    def __init__(self, skills_dir: str = "/skills"):
        self.skills_dir = skills_dir
        self.skills = []

    def load_skills(self):
        """Scans the directory for SKILL.md files and parses them."""
        self.skills = []
        if not os.path.exists(self.skills_dir):
            return

        for root, _, files in os.walk(self.skills_dir):
            if "SKILL.md" in files:
                skill_path = os.path.join(root, "SKILL.md")
                try:
                    with open(skill_path, "r") as f:
                        content = f.read()
                        self.skills.append(self._parse_skill(content))
                except Exception as e:
                    print(f"Error loading skill at {skill_path}: {e}")

    def _parse_skill(self, content: str):
        """Parses frontmatter and body from markdown content."""
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2]
                return {"frontmatter": frontmatter, "body": body}
            except yaml.YAMLError:
                pass
        return {"frontmatter": {}, "body": content}

    def get_formatted_context(self) -> str:
        """Returns all skills as a formatted string for LLM context."""
        if not self.skills:
            self.load_skills()
            
        context = "# Available Skills\n\n"
        for skill in self.skills:
            name = skill['frontmatter'].get('name', 'Unknown Skill')
            description = skill['frontmatter'].get('description', '')
            context += f"## {name}\n"
            context += f"{description}\n\n"
            context += f"{skill['body']}\n\n"
        return context

# Instantiate for easy import
skills_loader = SkillsLoader()
