from colored import fg, attr

def display_color(code, description):
    print(f"{fg(code)}{description}{attr(0)}")

def display_all_colors():
    print("Displaying all colors supported by the 'colored' library:")
    print("------------------------------------------------------")
    for code in range(256):
        description = f"Color {code}"
        display_color(code, description)

if __name__ == "__main__":
    display_all_colors()
