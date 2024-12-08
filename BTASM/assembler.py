import sys

instructionOrder = 0

# Instruction set and their corresponding opcodes
INSTRUCTION_SET = {
    "mov": "00", "dest": "01", "str": "02", "ld": "03", "mrr": "04", "jz": "05",
    "swp": "06", "add": "07", "sub": "08", "and": "09", "or": "0A", "xor": "0B",
    "not": "0C", "dsbx": "0D", "jmp": "0E", "pbcx": "0F", "jmpi": "10", "jzi": "11",
    "cmp": "12"
}

# Registers and their corresponding binary codes
REGISTER_CODES = {
    "AX": "0000", "BX": "0001", "CX": "0002", "RR": "0003"
}

# Function to assemble a single line of code (first pass)
def first_pass(line, labels, address):
    line = line.strip()
    if not line or line.startswith(";") or line.startswith("."):  # Ignore empty lines, directives, and comments
        return address

    parts = line.split()

    if parts[0].startswith("-"):  # Label definition
        label_name = parts[0]  # Label names start with '-'
        labels[label_name] = address
        # In first_pass
        print(f"First pass - found label: {label_name} at address {address}")
        return address  # Don't increment address for labels in the first pass

    # Handle normal instructions
    return address + 1  # Increment address by 1 for each instruction

# Function to assemble a single line of code (second pass)
def second_pass(line, labels, address):
    global instructionOrder
    line = line.strip()
    if not line or line.startswith(";") or line.startswith("."):  # Ignore empty lines, directives, and comments
        if line.startswith("."):
            instructionOrder = 0 if line == ".operandFirst" else 1
        return None, address

    parts = line.split()

    if parts[0].startswith("-"):  # Label definition (not needed in the second pass)
        return None, address

    # Handle normal instructions
    opcode = INSTRUCTION_SET.get(parts[0])
    if not opcode:
        raise ValueError(f"Unknown instruction: {parts[0]}")

    # Process operands
    operand_values = []
    for op in parts[1:]:
        if op.startswith("-"):  # It's a label reference
            label_address = labels.get(op)
            if label_address is None:
                raise ValueError(f"Label {op} not defined.")
            operand_values.append(f"{label_address:04X}")
        else:  # It's a register or value
            operand_values.append(REGISTER_CODES.get(op.upper(), f"{int(op, 16):04X}" if op.startswith("0x") else f"{int(op):04X}" if op.isnumeric() else None))
        
    if None in operand_values:
        raise ValueError(f"Invalid operand: {parts[1:]}")
    
    if not operand_values:
        operand_values = ["0000"]

    # In second_pass
    print(f"Second pass - processing instruction: {line}, with operands: {operand_values}")

    machine_code = (opcode + "".join(operand_values) if instructionOrder == 1 else "".join(operand_values) + opcode)
    return machine_code, address + 1  # Increment address by 1 for the next instruction

# Function to assemble the entire program
def assemble_program(source_code):
    labels = {}  # Store label names and their corresponding addresses
    machine_code = []
    address = 0  # Reset address for final code

    # First pass: Identify labels and calculate the address
    for line in source_code.splitlines():
        address = first_pass(line, labels, address)

    # Second pass: Generate machine code and resolve labels
    address = 0  # Reset address for machine code generation
    for line in source_code.splitlines():
        assembled_line, address = second_pass(line, labels, address)
        if assembled_line:
            machine_code.append(assembled_line)

    return machine_code

# Main entry point
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: assembler.py <input_file> <output_file>")
        sys.exit(1)

    with open(sys.argv[1], "r") as file:
        source_code = file.read()

    machine_code = assemble_program(source_code)

    with open(sys.argv[2], "wb") as file:
        for line in machine_code:
            for byte in [int(line[i:i+2], 16) for i in range(0, len(line), 2)]:
                file.write(byte.to_bytes(1, byteorder='big'))

    print(f"Assembly complete. Machine code written to {sys.argv[2]}")
