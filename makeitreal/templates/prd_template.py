"""Amazon Working Backwards PRD template implementation."""

import re
from typing import Any

from ..models import PRDSection, UserStory


class PRDTemplate:
    """Amazon Working Backwards PRD template generator and parser."""

    def __init__(self) -> None:
        """Initialize PRD template with Amazon Working Backwards structure."""
        self.template = self._get_template()

    def _get_template(self) -> str:
        """Get the Amazon Working Backwards PRD template."""
        return """
# Product Requirements Document

## Press Release (Working Backwards)

**Headline**: [Compelling product headline]

**Subtitle**: [Brief subtitle explaining the value]

**Introduction**: [3-4 sentences describing what the product does and why customers will love it]

**Problem**: [Top 2-3 customer problems this product solves]

**Solution**: [How your product uniquely solves these problems]

**Leader Quote**: [Quote from company leader about the product vision]

**How It Works**: [Brief explanation of how customers will use the product]

**Customer Quote**: [Quote from target customer about the value they receive]

**Call to Action**: [How customers can get started]

## Frequently Asked Questions

### Internal FAQs
- **Question**: [Internal question about implementation, resources, etc.]
  **Answer**: [Detailed internal answer]

### Customer FAQs
- **Question**: [Customer question about features, usage, etc.]
  **Answer**: [Customer-facing answer]

## Technical Requirements

### Core Features
- [Priority feature 1]
- [Priority feature 2]
- [Priority feature 3]

### User Stories
[Generate INVEST-compliant user stories]

### Success Metrics
- [Key metric 1]
- [Key metric 2]
- [Key metric 3]

### Timeline
[Estimated development phases and timeline]
"""

    def get_template(self) -> str:
        """Return the complete PRD template."""
        return self.template

    def parse_sections(self, content: str) -> list[PRDSection]:
        """Parse PRD content into structured sections."""
        sections = []

        # Split content by headers (# or ##)
        header_pattern = r"^(#{1,3})\s+(.+)$"
        lines = content.split("\n")

        current_section = None
        current_content = []

        for line in lines:
            match = re.match(header_pattern, line)
            if match:
                # Save previous section if exists
                if current_section:
                    sections.append(
                        PRDSection(
                            title=current_section, content="\n".join(current_content).strip()
                        )
                    )

                # Start new section
                current_section = match.group(2)
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Add final section
        if current_section:
            sections.append(
                PRDSection(title=current_section, content="\n".join(current_content).strip())
            )

        return sections

    def extract_user_stories(self, content: str) -> list[UserStory]:
        """Extract user stories from PRD content."""
        stories = []

        # Look for user story patterns: "As a ... I want ... So that ..."
        story_pattern = (
            r"(?:^|\n)(?:-\s*)?As\s+a\s+(.+?),?\s+I\s+want\s+(.+?),?\s+so\s+that\s+(.+?)(?:\n|$)"
        )
        matches = re.finditer(story_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)

        for _i, match in enumerate(matches, 1):
            user_type = match.group(1).strip()
            capability = match.group(2).strip()
            benefit = match.group(3).strip()

            title = f"As a {user_type}, I want {capability}"
            description = f"So that {benefit}"

            story = UserStory(
                title=title,
                description=description,
                acceptance_criteria=[
                    f"Given that I am a {user_type}",
                    f"When I {capability}",
                    f"Then I should be able to {benefit}",
                ],
                definition_of_done=[
                    "Code implemented and reviewed",
                    "Unit tests written and passing",
                    "Integration tests passing",
                    "Documentation updated",
                ],
                priority="medium",
                estimate="",
            )
            stories.append(story)

        return stories

    def extract_press_release(self, content: str) -> dict[str, str]:
        """Extract press release sections from content."""
        press_release = {}

        # Extract sections using regex patterns
        patterns = {
            "headline": r"\*\*Headline\*\*:\s*(.+?)(?:\n|$)",
            "subtitle": r"\*\*Subtitle\*\*:\s*(.+?)(?:\n|$)",
            "intro": r"\*\*Introduction\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "problem": r"\*\*Problem\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "solution": r"\*\*Solution\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "leader_quote": r"\*\*Leader Quote\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "how_it_works": r"\*\*How It Works\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "customer_quote": r"\*\*Customer Quote\*\*:\s*(.+?)(?:\n\n|\*\*)",
            "call_to_action": r"\*\*Call to Action\*\*:\s*(.+?)(?:\n\n|\*\*)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                press_release[key] = match.group(1).strip()
            else:
                press_release[key] = ""

        return press_release

    def extract_faq(self, content: str) -> dict[str, list[str]]:
        """Extract FAQ sections from content."""
        faq = {"internal": [], "customer": []}

        # Find FAQ sections
        internal_section = re.search(
            r"### Internal FAQs\s*(.+?)(?=### Customer FAQs|$)", content, re.DOTALL | re.IGNORECASE
        )

        customer_section = re.search(
            r"### Customer FAQs\s*(.+?)(?=##|$)", content, re.DOTALL | re.IGNORECASE
        )

        # Extract Q&A pairs
        qa_pattern = r"-\s*\*\*Question\*\*:\s*(.+?)\s*\*\*Answer\*\*:\s*(.+?)(?=\n-|\n\n|$)"

        if internal_section:
            matches = re.finditer(qa_pattern, internal_section.group(1), re.DOTALL)
            for match in matches:
                faq["internal"].append(f"Q: {match.group(1).strip()}\nA: {match.group(2).strip()}")

        if customer_section:
            matches = re.finditer(qa_pattern, customer_section.group(1), re.DOTALL)
            for match in matches:
                faq["customer"].append(f"Q: {match.group(1).strip()}\nA: {match.group(2).strip()}")

        return faq

    def extract_technical_requirements(self, content: str) -> list[str]:
        """Extract technical requirements from content."""
        requirements = []

        # Find technical requirements section
        tech_section = re.search(
            r"### Core Features\s*(.+?)(?=### User Stories|###|$)",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        if tech_section:
            # Extract bullet points
            bullet_pattern = r"-\s*(.+?)(?=\n-|\n\n|$)"
            matches = re.finditer(bullet_pattern, tech_section.group(1), re.DOTALL)
            for match in matches:
                requirement = match.group(1).strip()
                if requirement and not requirement.startswith("["):
                    requirements.append(requirement)

        return requirements

    def extract_success_metrics(self, content: str) -> list[str]:
        """Extract success metrics from content."""
        metrics = []

        # Find success metrics section
        metrics_section = re.search(
            r"### Success Metrics\s*(.+?)(?=### Timeline|###|$)", content, re.DOTALL | re.IGNORECASE
        )

        if metrics_section:
            # Extract bullet points
            bullet_pattern = r"-\s*(.+?)(?=\n-|\n\n|$)"
            matches = re.finditer(bullet_pattern, metrics_section.group(1), re.DOTALL)
            for match in matches:
                metric = match.group(1).strip()
                if metric and not metric.startswith("["):
                    metrics.append(metric)

        return metrics

    def extract_timeline(self, content: str) -> str:
        """Extract timeline from content."""
        # Find timeline section
        timeline_section = re.search(
            r"### Timeline\s*(.+?)(?=##|$)", content, re.DOTALL | re.IGNORECASE
        )

        if timeline_section:
            return timeline_section.group(1).strip()

        return ""

    def parse_complete_spec(self, content: str) -> dict[str, Any]:
        """Parse complete PRD content into TechnicalSpec format."""
        return {
            "press_release": self.extract_press_release(content),
            "faq": self.extract_faq(content),
            "user_stories": [story.model_dump() for story in self.extract_user_stories(content)],
            "technical_requirements": self.extract_technical_requirements(content),
            "success_metrics": self.extract_success_metrics(content),
            "timeline": self.extract_timeline(content),
            "sections": [section.model_dump() for section in self.parse_sections(content)],
        }
