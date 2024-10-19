from printer_proxy import PrinterProxy


def main() -> None:
    p = PrinterProxy("Alice")
    print(f"名前は現在{p.get_printer_name()}です。")
    p.set_printer_name("Bob")
    print(f"名前は現在{p.get_printer_name()}です。")
    p.print("Hello, world.")


if __name__ == "__main__":
    main()
