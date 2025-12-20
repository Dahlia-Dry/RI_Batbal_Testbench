import time
import runpy

def coerce_type(value, expected_type):
    if value is None:
        return None

    if expected_type == "int":
        return int(value)

    if expected_type == "float":
        return float(value)

    if expected_type == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("1", "true", "yes", "on")
        return bool(value)

    if expected_type == "string":
        return str(value)

    if expected_type == "list":
        if isinstance(value, list):
            return value
        return [value]

    if expected_type == "dict":
        if isinstance(value, dict):
            return value
        raise TypeError(f"Expected dict, got {type(value)}")

    raise ValueError(f"Unsupported type in schema: {expected_type}")


def execute_step(step, inst, last_result):
    if "delay_before" in step:
        time.sleep(step["delay_before"])

    action = step["action"]
    print(f"[DEBUG] action={step['action']} last_result={last_result!r} ({type(last_result)})")

    result = None

    resolved_step = {}

    for key, value in step.items():

        if value == "$last":
            if last_result is None:
                raise ValueError("No last_result available")
            resolved_step[key] = last_result
            continue

        if isinstance(value, str) and value.startswith("$last."):
            if last_result is None:
                raise ValueError("No last_result available")
            if not isinstance(last_result, dict):
                raise TypeError(
                    f"$last is not a dict, cannot access field in {value}"
                )
            field = value[len("$last."):]
            resolved_step[key] = last_result[field]
            continue

        if isinstance(value, list):
            resolved_list = []
            for v in value:
                if v == "$last":
                    if last_result is None:
                        raise ValueError("No last_result available")
                    resolved_list.append(last_result)

                elif isinstance(v, str) and v.startswith("$last."):
                    if last_result is None:
                        raise ValueError("No last_result available")
                    if not isinstance(last_result, dict):
                        raise TypeError(
                            f"$last is not a dict, cannot access field in {v}"
                        )
                    field = v[len("$last."):]
                    resolved_list.append(last_result[field])

                else:
                    resolved_list.append(v)

            resolved_step[key] = resolved_list
            continue

        resolved_step[key] = value

    step = resolved_step


    # ------------------------------------------------------------------
    # KEYSIGHT E36312 ACTIONS
    # ------------------------------------------------------------------

    if action == "psu_configure":
        result = inst.configure_psu(
            channel=step["channel"],
            current_limit=step.get("current_limit"),
            voltage_limit=step.get("voltage_limit"),
            output_enabled=step.get("output_enabled", False),
            sense_mode=step.get("sense_mode", "local"),
        )

    elif action == "psu_set_power":
        result = inst.set_power(
            ch=step["channel"],
            voltage=step["voltage"],
            current_limit=step["current_limit"],
            ramp_time=step.get("ramp_time", 0.0),
        )

    elif action == "psu_ramp_voltage":
        result = inst.ramp_voltage(
            ch=step["channel"],
            target_voltage=step["target_voltage"],
            ramp_time=step["ramp_time"],
        )

    elif action == "psu_measure_voltage":
        result = inst.measure_voltage(step["channel"])

    elif action == "psu_measure_current":
        result = inst.measure_current(step["channel"])

    elif action == "psu_measure_power":
        result = inst.measure_power(step["channel"])

    # ------------------------------------------------------------------
    # KEITHLEY 2450 SMU ACTIONS
    # ------------------------------------------------------------------

    elif action == "smu_reset":
        result = inst.smu_reset()

    elif action == "smu_zero_output":
        result = inst.smu_zero_output()

    elif action == "smu_configure":
        result = inst.smu_configure(
            source_function=step["source_function"],
            source_level=step["source_level"],
            compliance_limit=step["compliance_limit"],
            measure_function=step["measure_function"],
            sense_mode=step.get("sense_mode", "2w"),
            output_enabled=step.get("output_enabled", False),
        )

    elif action == "smu_set_source":
        result = inst.smu_set_source(
            source_function=step["source_function"],
            level=step["level"],
            compliance_limit=step["compliance_limit"],
            output_enabled=step.get("output_enabled", True),
        )

    elif action == "smu_set_output":
        result = inst.smu_set_output(
            enabled=step["enabled"]
        )

    elif action == "smu_measure_voltage":
        result = inst.smu_measure_voltage()

    elif action == "smu_measure_current":
        result = inst.smu_measure_current()

    elif action == "smu_sweep":
        result = inst.smu_sweep(
            start=step["start"],
            stop=step["stop"],
            step=step["step"],
            delay=step.get("delay", 0.0),
            save_to=step.get("save_to"),
        )

    # ------------------------------------------------------------------
    # RIGOL DG1062Z ACTIONS
    # ------------------------------------------------------------------

    elif action == "wavegen_start_waveform":
        result = inst.start_waveform(
            channel=step["channel"],
            waveform=step["waveform"],
            output=step.get("output"),
        )

    elif action == "wavegen_configure_output":
        result = inst.configure_output(
            channel=step["channel"],
            impedance=step.get("impedance"),
            enabled=step.get("enabled"),
        )

    elif action == "wavegen_stop_waveform":
        result = inst.configure_output(
            channel=step["channel"],
            enabled=False,
        )

    # ------------------------------------------------------------------
    # TEKTRONIX MSO58 ACTIONS
    # ------------------------------------------------------------------

    elif action == "scope_configure":
        result = inst.configure_scope(
            trigger=step["trigger"],
            channels=step["channels"],
            timebase=step["timebase"],
            measurements=step["measurements"]
        )

    elif action == "scope_capture":
        result = inst.capture(
            channels=step["channels"],
            duration=step["duration"],
            save_to=step["save_to"],
            show_plot=step.get("show_plot",False)
        )

    elif action == "scope_screenshot":
        result = inst.screenshot(
            save_to=step["save_to"]
        )

    #----------------------------------------------------------------
    # NI VIRTUALBENCH ACTIONS
    #---------------------------------------------------------------- 

    elif action == "vb_psu_configure":
        result = inst.vb_psu_configure(
            channel=step["channel"],
            voltage=step.get("voltage"),
            current_limit=step.get("current_limit"),
            output_enabled=step.get("output_enabled", False),
        )

    elif action == "vb_psu_set_power":
        result = inst.vb_psu_set_power(
            channel=step["channel"],
            voltage=step["voltage"],
            current_limit=step["current_limit"],
        )

    elif action == "vb_psu_enable":
        result = inst.vb_psu_enable(
            channel=step["channel"],
            enable=step.get("enable", True),
        )

    # ---------------- Waveform Generator ----------------

    elif action == "vb_wavegen_start_waveform":
        result = inst.vb_wavegen_start_waveform(
            waveform=step["waveform"],
            output=step.get("output"),
        )

    elif action == "vb_wavegen_stop_waveform":
        result = inst.vb_wavegen_stop_waveform()

    # ---------------- Digital IO ----------------

    elif action == "vb_dio_configure":
        result = inst.vb_dio_configure(
            lines=step["lines"],
            direction=step["direction"],
        )

    elif action == "vb_dio_write":
        result = inst.vb_dio_write(
            lines=step["lines"],
            values=step["values"],
        )

    elif action == "vb_dio_read":
        result = inst.vb_dio_read(
            lines=step["lines"]
        )

    # ------------------------------------------------------------------
    # SCRIPT ACTION
    # ------------------------------------------------------------------

    elif action == "run_script":
        if "script" not in step:
            raise ValueError("run_script requires 'script'")

        globals_dict = {
            "input_data": last_result,
        }

        result = runpy.run_path(step["script"], init_globals=globals_dict)
        result = result.get("OUTPUT")

    else:
        raise ValueError(f"Unknown action: {action}")

    if "delay_after" in step:
        time.sleep(step["delay_after"])

    return result
