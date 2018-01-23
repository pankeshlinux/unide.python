# Copyright (c) 2017 Contact Software.
#
# All rights reserved. This program and the accompanying materials are
# made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution.
#
# The Eclipse Public License is available at
#     http://www.eclipse.org/legal/epl-v10.html

from datetime import datetime
import dateutil.tz

from unide.util import dumps
from unide.process import (ProcessPayload, Part, Process, Program,
                           Measurement, SpecialValue)
from unide.common import Device


def test_process():
    Process()


def test_build_sample():
    device = Device("a4927dad-58d4-4580-b460-79cefd56775b",
                    operationalStatus="normal",
                    swVersion="2.0.3.13",
                    swBuildId="41535")
    part = Part('SINGLE',
                partTypeID="F00VH07328",
                partID="420003844",
                result="NOK",
                code="HUH289",
                toolId="32324-432143")
    tz_plus2 = dateutil.tz.tzoffset("+02:00", 2 * 60 * 60)
    ts = datetime(2002, 5, 30, 9, 30, 10, 123*1000, tz_plus2)
    process = Process(externalProcessId="b4927dad-58d4-4580-b460-79cefd56775b",
                      ts=ts,
                      result="NOK",
                      shutoffPhase="phase 1",
                      program=Program("1", "Programm 1", lastChangedDate=ts),
                      name="Getriebedeckel verschrauben")
    payload = ProcessPayload(
        device=device,
        part=part,
        process=process)
    payload.process.shutoffValues.add_dimension("force")
    payload.process.shutoffValues.add_dimension("pressure")
    payload.process.shutoffValues.force.ts = ts
    payload.process.shutoffValues.force.value = 24
    payload.process.shutoffValues.force.upperError = 26
    payload.process.shutoffValues.force.lowerError = 22
    payload.process.shutoffValues.pressure.value = 50
    payload.process.shutoffValues.pressure.upperError = 52
    payload.process.shutoffValues["pressure"].lowerError = 48

    m = Measurement(ts=ts,
                    phase="phasen name 2",
                    name="500 Grad links drehen",
                    result="NOK",
                    code="0000 EE01")
    m.limits.add_dimension("temperature")
    m.limits.temperature.upperError = 4444
    m.limits.temperature.lowerError = 44
    m.limits.temperature.upperWarn = 2222
    m.limits.temperature.lowerWarn = 46
    m.specialValues.add_dimension("pressure")
    m.specialValues.add_dimension("force")
    m.specialValues.pressure.time = 24
    m.specialValues.pressure.value = 44.2432
    m.specialValues.force.time = 24
    m.specialValues.force.value = 24
    m.series.add_dimension("time")
    m.series.add_dimension("force")
    m.series.add_dimension("pressure")
    m.series.add_dimension("temperature")
    m.add_sample(time=0, force=26, pressure=52.4, temperature=45.4243)
    m.add_sample(time=23, force=23, pressure=46.32, temperature=46.42342)
    m.add_sample(time=24, force=24, pressure=44.2432, temperature=44.2432)

    payload.measurements.append(m)

    m = Measurement(ts=ts,
                    phase="phasen name",
                    result="OK")

    m.limits.add_dimension("force")
    m.limits.force.upperError = [27, 24, 25]
    m.limits.force.loweerError = [25, 22, 23]

    m.limits.add_dimension("pressure")
    m.limits.pressure.upperError = [54, 48, 46]
    m.limits.pressure.lowerError = [50, 44, 42]

    m.specialValues.add_dimension("pressure")
    m.specialValues.pressure.value = 24

    sv_force = SpecialValue(value=50)
    m.specialValues["force"] = sv_force

    m.series.add_dimension("time")
    m.series.add_dimension("force")
    m.series.add_dimension("pressure")
    m.series.add_dimension("temperature")
    m.add_sample(time=30, force=26, pressure=52.4, temperature=45.4243)
    m.add_sample(time=36, force=23, pressure=46.32, temperature=46.42342)
    m.add_sample(time=42, force=24, pressure=44.2432, temperature=44.2432)

    payload.measurements.append(m)

    assert len(list(m.samples())) == 3

    assert not payload.problems()

    payload.device._data["murx"] = 9
    errors = payload.problems()
    assert len(errors) == 1

    payload._data["content-spec"] = "wrong"
    errors = payload.problems()
    assert len(errors) == 2

    dumps(payload, indent=4)