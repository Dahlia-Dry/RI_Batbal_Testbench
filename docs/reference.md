# Testbench Reference

## Usage
### Running a test routine
Run a test sequence by providing a YAML configuration file:
`python run_test.py <testname>.yaml`

The YAML file defines the instruments to connect to and the sequence of actions to execute. Refer to the [README](README.md) for further info.

### Saving log file
Add the option `--save_log` to save the console output to a log file as `testbench_logs/<YYYYMMDD-HHMMSS-<testname>.log>`

### Viewing documentation
Use the `--help` option to view documentation directly from the command line:
- Show the overall reference: 
    `python run_test.py --help`
- Show documentation for a specific instrument: 
    `python run_test.py --help <InstrumentName>` 

