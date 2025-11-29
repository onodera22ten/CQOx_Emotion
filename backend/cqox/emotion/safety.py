"""
Safety Module for Emotion CQOx
High-risk text detection and resource provision
"""
import re
import hashlib
from typing import List, Tuple
from datetime import datetime

from .schemas import SafetyCheckResponse, SafetyResource


class SafetyGuard:
    """
    Safety guardrail for detecting high-risk content

    IMPORTANT: This is NOT a medical diagnostic tool.
    It's designed to detect obvious high-risk expressions and
    provide resources, not to make clinical judgments.
    """

    def __init__(self):
        # High-risk patterns (Japanese)
        self.critical_patterns = [
            r'死にたい',
            r'自殺',
            r'消えたい',
            r'生きている意味',
            r'死んだほうが',
        ]

        self.high_risk_patterns = [
            r'自傷',
            r'リストカット',
            r'もう無理',
            r'限界',
            r'助けて',
        ]

        self.medium_risk_patterns = [
            r'辛すぎる',
            r'しんどすぎる',
            r'眠れない.*日',
            r'食べられない',
        ]

        # Mental health resources (Japan)
        self.resources = [
            SafetyResource(
                name="いのちの電話",
                phone="0570-783-556",
                url="https://www.inochinodenwa.org/",
                description="24時間対応の電話相談"
            ),
            SafetyResource(
                name="こころの健康相談統一ダイヤル",
                phone="0570-064-556",
                url="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/seikatsuhogo/jisatsu/kokoro_dial.html",
                description="各都道府県の相談窓口につながります"
            ),
            SafetyResource(
                name="厚生労働省 SNS相談",
                url="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/seikatsuhogo/jisatsu/soudan_sns.html",
                description="LINE・チャットで相談できる窓口一覧"
            ),
        ]

    def check_text(self, text: str) -> SafetyCheckResponse:
        """
        Check text for high-risk content

        Returns SafetyCheckResponse with risk level and appropriate resources
        """
        if not text or len(text.strip()) == 0:
            return SafetyCheckResponse(
                is_safe=True,
                risk_level="none",
                triggers=[],
                resources=[]
            )

        # Detect patterns
        triggers = []
        risk_level = "none"

        # Critical patterns (highest priority)
        for pattern in self.critical_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                triggers.append(pattern)
                risk_level = "critical"

        # High risk patterns
        if risk_level != "critical":
            for pattern in self.high_risk_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    triggers.append(pattern)
                    risk_level = "high"

        # Medium risk patterns
        if risk_level not in ["critical", "high"]:
            for pattern in self.medium_risk_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    triggers.append(pattern)
                    risk_level = "medium"

        # Determine response
        is_safe = risk_level in ["none", "low"]

        if risk_level == "critical":
            message = """
大変つらい状況だと思います。Emotion CQOxは医療サービスではないため、
専門的なサポートをすぐに受けることをお勧めします。

以下の相談窓口では、専門の相談員があなたの話を聞きます。
一人で抱え込まず、まずは話してみてください。
            """.strip()
            resources = self.resources

        elif risk_level == "high":
            message = """
かなり辛い状況のようですね。もし必要であれば、
専門の相談窓口を利用することも検討してください。
            """.strip()
            resources = self.resources

        elif risk_level == "medium":
            message = """
辛い気持ちを抱えているようですね。
必要に応じて、専門の相談窓口もご利用いただけます。
            """.strip()
            resources = self.resources[:2]  # Provide fewer resources

        else:
            message = None
            resources = []

        return SafetyCheckResponse(
            is_safe=is_safe,
            risk_level=risk_level,
            triggers=triggers,
            message=message,
            resources=resources
        )

    def log_detection(
        self,
        user_id: int,
        text: str,
        risk_level: str,
        triggers: List[str]
    ) -> dict:
        """
        Log a safety detection event

        IMPORTANT: Do NOT store the actual text, only a hash
        """
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        return {
            "user_id": user_id,
            "text_hash": text_hash,  # NOT the actual text
            "risk_level": risk_level,
            "trigger_count": len(triggers),
            "timestamp": datetime.utcnow().isoformat()
        }
