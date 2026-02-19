from fvafk.c2a.gate_framework import GateOrchestrator, GateResult, GateStatus, PhonologicalGate


class EchoGate(PhonologicalGate):
    def apply(self, segments):
        return GateResult(status=GateStatus.ACCEPT, output=segments + ["echo"], reason="echoed")


class RejectGate(PhonologicalGate):
    def apply(self, segments):
        return GateResult(status=GateStatus.REJECT, output=segments, reason="reject")


def test_gate_orchestrator_runs_all_gates():
    gate = EchoGate("G_ECHO")
    orchestrator = GateOrchestrator([gate])
    output, results = orchestrator.run(["ب", "ت"])
    assert output == ["ب", "ت", "echo"]
    assert results[0].status == GateStatus.ACCEPT


def test_gate_orchestrator_stops_on_reject():
    gate1 = EchoGate("G_ECHO")
    gate2 = RejectGate("G_REJECT")
    gate3 = EchoGate("G_SHOULD_NOT_RUN")
    orchestrator = GateOrchestrator([gate1, gate2, gate3])
    output, results = orchestrator.run(["ف"])
    assert len(results) == 2
    assert results[-1].status == GateStatus.REJECT
