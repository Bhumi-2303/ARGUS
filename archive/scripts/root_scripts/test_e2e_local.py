import asyncio
from fastapi import FastAPI
from argus.services.common.schemas import AgentMessage
from argus.services.detector.main import detector_agent_instance, app as det_app
from argus.services.risk_agent.main import risk_agent_instance
from argus.services.decision_agent.main import decision_agent_instance

async def main():
    async with det_app.router.lifespan_context(det_app):
        print("Testing detector...")
        msg = AgentMessage(
            message_id="1", event_id="1", sender="Coord", receiver="Det",
            message_type="request", payload={"flow_record": {"pkt_mean_to_max": 0.95, "tcp_flag_density": 1.0, "log_pkt_mean": 4.2, "log_pkt_max": 4.3}}, trace_id="1"
        )
        res1 = await detector_agent_instance.process(msg)
        print("Detector:", res1.payload)
        
        print("Testing risk...")
        msg2 = AgentMessage(
            message_id="2", event_id="1", sender="Coord", receiver="Risk",
            message_type="request", payload={"asset_id": "SCADA-MTU-01", "probability": res1.payload["probability"]}, trace_id="1"
        )
        res2 = await risk_agent_instance.process(msg2)
        print("Risk:", res2.payload)
        
        print("Testing decision...")
        msg3 = AgentMessage(
            message_id="3", event_id="1", sender="Coord", receiver="Dec",
            message_type="request", payload={"prediction": res1.payload["prediction"], "probability": res1.payload["probability"], "shap_values": res1.payload["shap_values"], "risk_score": res2.payload["risk_score"], "risk_tier": res2.payload["risk_tier"], "attck_context": []}, trace_id="1"
        )
        res3 = await decision_agent_instance.process(msg3)
        print("Decision:", res3.payload)

asyncio.run(main())
