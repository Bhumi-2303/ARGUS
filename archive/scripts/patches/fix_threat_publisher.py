import sys

content = """
    async def publish(self, result: Any) -> None:
        if isinstance(result, ThreatAnalysisResult) and self.blackboard and self.message_bus:
            from argus.schemas.messages import ThreatEvent
            from argus.core.enums import BlackboardSection, TaskPriority
            from datetime import datetime
            import uuid

            threat_event = ThreatEvent(
                request_id=str(uuid.uuid4()),
                trace_id=result.source_event_id,
                agent_id=str(self.agent_id),
                timestamp=datetime.utcnow(),
                priority=TaskPriority.HIGH,
                event_type="THREAT_EVENT",
                attack_type="attack" if result.threat_level.value != "low" else "benign",
                severity=result.confidence,
                description=f"Predicted by {result.model_version} ({result.protocol_status})",
                implementation_status=result.protocol_status
            )
            
            await self.blackboard.write(
                section=BlackboardSection.THREAT_RESULTS,
                key=threat_event.trace_id,
                value=threat_event
            )
            
            await self.message_bus.publish(
                topic=f"events.threat.{result.threat_level.value}",
                message=threat_event
            )
"""

with open('src/argus/agents/threat_analysis/agent.py', 'r') as f:
    code = f.read()

import re
code = re.sub(r'    async def publish\(self, result: Any\) -> None:.*?            await self.message_bus.publish\(\n                topic=f"events.threat.{result.threat_level.value}",\n                message=threat_event\n            \)', content, code, flags=re.DOTALL)

with open('src/argus/agents/threat_analysis/agent.py', 'w') as f:
    f.write(code)
