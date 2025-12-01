import time

def execute_step(step, inst):
    if "delay_before" in step:
        time.sleep(step["delay_before"])

    action = step["action"]

    if action == "set_power":
        inst.set_power(
            ch=step["channel"],
            voltage=step["voltage"],
            current_limit=step["current_limit"],
            ramp_time=step.get("ramp_time", 0)
        )

    elif action == "start_waveform":
        inst.start_waveform(
            channel=step["channel"],
            waveform=step["waveform"],
            output=step.get("output", {})
        )

    elif action == "setup_scope":
        inst.setup_scope(
            trigger=step["trigger"],
            channels=step["channels"]
        )

    elif action == "capture":
        inst.capture(
            channels=step["channels"],
            duration=step["duration"],
            save_to=step["save_to"],
            show_plot=True
        )
    
    elif action == "screenshot":
        inst.screenshot(
            save_to=step["save_to"]
        )

    else:
        raise ValueError(f"Unknown action: {action}")

    if "delay_after" in step:
        time.sleep(step["delay_after"])
