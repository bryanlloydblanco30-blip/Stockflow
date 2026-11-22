from __future__ import annotations

import flet as ft


BG = "#FFF9EF"
SURFACE = "#FFFEFA"
INK = "#202334"
GREEN = "#245C45"
MUTED = "#69756B"
BORDER = "#E0DEC4"
PALE_GREEN = "#E5EFDB"
PALE_BLUE = "#D7EBFF"
PALE_PEACH = "#FFE2CD"
PALE_LAVENDER = "#EEE6F8"
PALE_YELLOW = "#FFF3CF"
PALE_ROSE = "#F9E9E3"

ASSETS = "assets"

NAV = [
    ("home", "Home", ft.Icons.HOME_OUTLINED, ft.Icons.HOME_ROUNDED),
    ("sell", "Sell", ft.Icons.SHOPPING_CART_OUTLINED, ft.Icons.SHOPPING_CART_ROUNDED),
    ("stock", "Stock", ft.Icons.INVENTORY_2_OUTLINED, ft.Icons.INVENTORY_2_ROUNDED),
    ("restock", "Restock", ft.Icons.LOCAL_SHIPPING_OUTLINED, ft.Icons.LOCAL_SHIPPING_ROUNDED),
    ("reports", "Reports", ft.Icons.BAR_CHART_OUTLINED, ft.Icons.BAR_CHART_ROUNDED),
]

META = {
    "home": ("Home", "Your store at a glance"),
    "sell": ("Sell", "Build a sale and checkout"),
    "stock": ("Stock", "Manage products and availability"),
    "restock": ("Restock", "Plan your next replenishment"),
    "reports": ("Reports", "Understand your store performance"),
    "sell_states": ("Sell states", "Checkout and inventory availability states"),
    "adjust": ("Adjust count · Fresh Milk 1L", "Update the physical count for this batch"),
    "history": ("Transaction history", "Review sales and inventory movements"),
}

PRODUCTS = [
    ("4800010001", "Pandesal pack", "Bread", "12", "₱32.00", "₱45.00", "Expires soon", "red"),
    ("4800010002", "Sardines 155g", "Canned", "3", "₱20.00", "₱28.00", "Low", "amber"),
    ("4800010003", "Bottled water 500ml", "Drinks", "48", "₱14.00", "₱25.00", "OK", "green"),
    ("4800010004", "Notebook", "School supplies", "20", "₱40.00", "₱58.00", "Untracked", "green"),
    ("4800010005", "Instant noodles", "Canned", "60", "₱9.00", "₱14.00", "OK", "green"),
    ("4800010006", "Loaf bread", "Bread", "9", "₱48.00", "₱65.00", "Near expiry", "amber"),
]


def text(value: str, size: int = 15, color: str = INK, weight=None, **kwargs) -> ft.Text:
    return ft.Text(value, size=size, color=color, weight=weight, **kwargs)


def rounded_button(
    label: str,
    on_click=None,
    bgcolor: str = SURFACE,
    color: str = INK,
    icon=None,
    width: int | None = None,
    disabled: bool = False,
) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        text=label,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        width=width,
        height=48,
        style=ft.ButtonStyle(
            bgcolor=bgcolor,
            color=color,
            shape=ft.RoundedRectangleBorder(radius=24),
            padding=ft.padding.symmetric(horizontal=24),
            elevation=0,
        ),
    )


def card(content, bgcolor: str = SURFACE, padding: int = 24, expand=False, **kwargs) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=ft.border.all(1, BORDER),
        border_radius=30,
        padding=padding,
        expand=expand,
        **kwargs,
    )


def stat_card(label: str, value: str, bgcolor: str = SURFACE, value_color: str = INK) -> ft.Container:
    return card(
        ft.Column(
            [
                text(label, 13, MUTED, ft.FontWeight.W_600),
                text(value, 28, value_color, ft.FontWeight.BOLD),
            ],
            spacing=18,
        ),
        bgcolor=bgcolor,
        padding=24,
        expand=True,
        height=145,
    )


def badge(label: str, tone: str = "green") -> ft.Container:
    tones = {
        "green": ("#D8F0DF", "#175E36"),
        "red": ("#FFDCE1", "#C30023"),
        "amber": ("#FFEDC9", "#8C5100"),
    }
    bg, fg = tones.get(tone, tones["green"])
    return ft.Container(
        text(label, 12, fg),
        bgcolor=bg,
        border_radius=18,
        padding=ft.padding.symmetric(horizontal=14, vertical=5),
        alignment=ft.alignment.center,
    )


class StockFlow:
    def __init__(self, page: ft.Page):
        self.page = page
        self.route = "start"
        self.stock_filter = "All"
        self.stock_query = ""
        self.report_period = "Week"
        self.history_filter = "All"
        self.cart = [
            {"name": "Pandesal pack", "qty": 1, "price": 45},
            {"name": "Sardines 155g", "qty": 2, "price": 28},
            {"name": "Bottled water 500ml", "qty": 1, "price": 25},
            {"name": "Notebook", "qty": 1, "price": 58},
        ]

        page.title = "StockFlow"
        page.bgcolor = BG
        page.padding = 0
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(
            color_scheme_seed=GREEN,
            use_material3=True,
            font_family="Inter",
        )
        page.fonts = {
            "Inter": "https://static.figma.com/font/Inter_1",
            "SF Pro Rounded": "https://static.figma.com/font/SF-Pro-Rounded-Bold_1",
        }
        page.on_resized = self.on_resize
        self.render()

    def go(self, route: str):
        def handler(_=None):
            self.route = route
            self.render()

        return handler

    def on_resize(self, _):
        self.render()

    @property
    def compact(self) -> bool:
        return bool(self.page.width and self.page.width < 920)

    def render(self):
        self.page.controls.clear()
        if self.route == "start":
            self.page.add(self.start_page())
        else:
            self.page.add(self.app_shell())
        self.page.update()

    def start_page(self) -> ft.Control:
        story = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Image(src=f"{ASSETS}/ea9fe.svg", width=48, height=48),
                            text("StockFlow", 13, "#5D765D"),
                        ],
                        spacing=18,
                    ),
                    ft.Container(height=38),
                    text(
                        "Your store.\nA little happier.",
                        52 if not self.compact else 40,
                        GREEN,
                        ft.FontWeight.BOLD,
                        font_family="SF Pro Rounded",
                    ),
                    text("Everything you need for a good day of shopkeeping.", 17, MUTED),
                    ft.Image(
                        src=f"{ASSETS}/051ce.svg",
                        width=600 if not self.compact else None,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    text("Small shop. Big possibilities.", 22, GREEN, ft.FontWeight.BOLD),
                    text(
                        "Sell, restock, and keep your business growing — all in one place.",
                        15,
                        MUTED,
                    ),
                ],
                spacing=18,
            ),
            expand=True,
        )
        choices = ft.Column(
            [
                text("StockFlow", 27, GREEN, ft.FontWeight.BOLD, font_family="SF Pro Rounded"),
                text("Choose where you’d like to start.", 16, MUTED),
                ft.Container(height=18),
                *[
                    rounded_button(
                        label,
                        self.go(route),
                        GREEN if route == "home" else "#F3F5EC",
                        "#FFFFFF" if route == "home" else GREEN,
                        icon=active if route == "home" else icon,
                        width=340,
                    )
                    for route, label, icon, active in NAV
                ],
            ],
            spacing=14,
        )
        choice_card = card(choices, padding=48, width=440)
        content = (
            ft.Column([story, choice_card], spacing=32)
            if self.compact
            else ft.Row([story, choice_card], spacing=70, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )
        return ft.Container(
            content,
            padding=ft.padding.symmetric(horizontal=36 if self.compact else 100, vertical=52),
            expand=True,
        )

    def app_shell(self) -> ft.Control:
        content = ft.Column(
            [self.header(), self.current_view()],
            spacing=22,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        if self.compact:
            return ft.Column(
                [
                    self.mobile_nav(),
                    ft.Container(content, padding=20, expand=True),
                ],
                spacing=0,
                expand=True,
            )
        return ft.Row(
            [
                ft.Container(self.sidebar(), width=268, padding=24),
                ft.Container(content, expand=True, padding=ft.padding.only(top=38, right=44, bottom=44)),
            ],
            spacing=34,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def active_section(self) -> str:
        return {
            "sell_states": "sell",
            "adjust": "stock",
            "history": "reports",
        }.get(self.route, self.route)

    def sidebar(self) -> ft.Control:
        active = self.active_section()
        nav_controls = []
        for route, label, icon, active_icon in NAV:
            selected = active == route
            nav_controls.append(
                ft.ListTile(
                    leading=ft.Icon(active_icon if selected else icon, color="#FFFFFF" if selected else GREEN),
                    title=text(label, 15, "#FFFFFF" if selected else "#4E7666", ft.FontWeight.W_500),
                    bgcolor=GREEN if selected else None,
                    shape=ft.RoundedRectangleBorder(radius=26),
                    on_click=self.go(route),
                )
            )
        return card(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Image(src=f"{ASSETS}/18451.svg", width=42, height=42),
                            ft.Column(
                                [
                                    text("StockFlow", 16, INK, ft.FontWeight.W_600),
                                    text("POINT OF SALE", 9, MUTED),
                                ],
                                spacing=2,
                            ),
                        ]
                    ),
                    ft.Container(height=42),
                    *nav_controls,
                    ft.Container(height=20),
                    ft.Image(src=f"{ASSETS}/45491.svg", height=132, fit=ft.ImageFit.CONTAIN),
                    ft.Container(
                        ft.Column(
                            [
                                ft.Icon(ft.Icons.HOME_OUTLINED, color=GREEN),
                                text("Made for the\ncorner of the world.", 14, GREEN),
                            ]
                        ),
                        bgcolor="#FFE8D7",
                        border=ft.border.all(1, "#F3C9AD"),
                        border_radius=28,
                        padding=20,
                    ),
                    ft.Container(expand=True),
                    rounded_button("Back", self.go("start"), width=190),
                ],
                spacing=8,
                expand=True,
            ),
            padding=18,
            expand=True,
        )

    def mobile_nav(self) -> ft.Control:
        active = self.active_section()
        return ft.NavigationBar(
            selected_index=next((i for i, item in enumerate(NAV) if item[0] == active), 0),
            bgcolor=SURFACE,
            indicator_color=PALE_GREEN,
            on_change=lambda e: self.go(NAV[e.control.selected_index][0])(),
            destinations=[
                ft.NavigationBarDestination(icon=icon, selected_icon=active_icon, label=label)
                for _, label, icon, active_icon in NAV
            ],
        )

    def header(self) -> ft.Control:
        title, subtitle = META[self.route]
        menu = ft.PopupMenuButton(
            content=rounded_button("More⌄", width=150),
            items=[
                ft.PopupMenuItem(text="Sell states", on_click=self.go("sell_states")),
                ft.PopupMenuItem(text="Adjust stock", on_click=self.go("adjust")),
                ft.PopupMenuItem(text="History", on_click=self.go("history")),
            ],
        )
        return ft.Row(
            [
                ft.Column(
                    [
                        text("YOUR STORE, SIMPLIFIED", 10, "#778579"),
                        text(title, 34 if not self.compact else 28, INK, ft.FontWeight.BOLD, font_family="SF Pro Rounded"),
                        text(subtitle, 15, MUTED),
                    ],
                    spacing=8,
                ),
                menu,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def current_view(self) -> ft.Control:
        return {
            "home": self.home,
            "sell": self.sell,
            "stock": self.stock,
            "restock": self.restock,
            "reports": self.reports,
            "sell_states": self.sell_states,
            "adjust": self.adjust,
            "history": self.history,
        }[self.route]()

    def home(self) -> ft.Control:
        stats = ft.ResponsiveRow(
            [
                ft.Container(stat_card("Today's Sales", "₱4,860.00", PALE_YELLOW), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("Today's Profit", "₱1,120.00", PALE_GREEN, "#1D6538"), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("Low Stock Items", "7", PALE_PEACH), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("Near Expiry Batches", "4", PALE_LAVENDER), col={"sm": 6, "lg": 3}),
            ],
            spacing=16,
            run_spacing=16,
        )
        rows = [
            ("Pandesal pack", "Expires in 1 day", badge("Red", "red")),
            ("Canned sardines 155g", "3 units left", badge("Amber", "amber")),
            ("Bottled water 500ml", "Reorder level reached", badge("Amber", "amber")),
            ("Loaf bread", "Expires in 3 days", badge("Amber", "amber")),
            ("Pencil HB", "6 units left", badge("Low")),
        ]
        table = self.data_table(["Product", "Issue", "Urgency"], rows)
        callout = card(
            ft.Row(
                [
                    ft.Column(
                        [
                            text("Ready for your next customer?", 20, GREEN),
                            text("Start a sale, check your shelves, and keep things moving.", 14, MUTED),
                        ]
                    ),
                    ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=GREEN),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=PALE_GREEN,
        )
        return ft.Column(
            [
                ft.Row([ft.Container(expand=True), rounded_button("START SALE", self.go("sell"), PALE_PEACH, GREEN)]),
                stats,
                card(ft.Column([text("Needs attention", 20, INK, ft.FontWeight.W_600), table])),
                ft.GestureDetector(content=callout, on_tap=self.go("sell")),
            ],
            spacing=24,
        )

    def sell(self) -> ft.Control:
        total = sum(item["qty"] * item["price"] for item in self.cart)
        items = []
        for i, item in enumerate(self.cart):
            items.append(
                ft.Row(
                    [
                        ft.Container(text(item["name"]), expand=2),
                        ft.Row(
                            [
                                ft.IconButton(ft.Icons.REMOVE, on_click=self.change_qty(i, -1)),
                                text(str(item["qty"])),
                                ft.IconButton(ft.Icons.ADD, on_click=self.change_qty(i, 1)),
                            ],
                            spacing=0,
                        ),
                        ft.Container(text(f"₱{item['price']:.2f}"), expand=1),
                        ft.Container(text(f"₱{item['price'] * item['qty']:.2f}"), expand=1),
                        rounded_button("Remove", self.remove_item(i), PALE_LAVENDER),
                    ],
                    spacing=8,
                )
            )
            items.append(ft.Divider(color="#EBE8E1", height=1))
        cart = card(
            ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            ft.TextField(hint_text="Scan or type barcode", col={"sm": 12, "md": 7}),
                            ft.Container(rounded_button("Scan", bgcolor=PALE_BLUE), col={"sm": 6, "md": 2}),
                            ft.Container(rounded_button("Simulate", bgcolor=PALE_LAVENDER), col={"sm": 6, "md": 3}),
                        ]
                    ),
                    *items,
                ],
                spacing=14,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
        )
        summary = card(
            ft.Column(
                [
                    text("Summary", 14, MUTED, ft.FontWeight.W_600),
                    self.summary_line("Items", str(sum(i["qty"] for i in self.cart))),
                    self.summary_line("Subtotal", f"₱{total:.2f}"),
                    self.summary_line("Tax 0%", "₱0.00"),
                    ft.Divider(),
                    self.summary_line("Total", f"₱{total:.2f}", True),
                    rounded_button("Checkout (Enter)", bgcolor=PALE_BLUE, width=300),
                ],
                spacing=14,
            )
        )
        side = ft.Column(
            [
                summary,
                card(
                    ft.Column(
                        [
                            text("A smooth checkout,\na happy customer.", 20, GREEN),
                            text("Scan items, review, and you’re ready.", 13, MUTED),
                        ]
                    ),
                    bgcolor=PALE_GREEN,
                ),
            ],
            width=None if self.compact else 330,
        )
        return ft.Column([cart, side], spacing=18) if self.compact else ft.Row([cart, side], spacing=22, vertical_alignment=ft.CrossAxisAlignment.START)

    def change_qty(self, index: int, amount: int):
        def handler(_):
            self.cart[index]["qty"] = max(1, self.cart[index]["qty"] + amount)
            self.render()

        return handler

    def remove_item(self, index: int):
        def handler(_):
            self.cart.pop(index)
            self.render()

        return handler

    @staticmethod
    def summary_line(label: str, value: str, large: bool = False) -> ft.Control:
        return ft.Row(
            [
                text(label, 16 if large else 14),
                text(value, 26 if large else 14, INK, ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def stock(self) -> ft.Control:
        query = self.stock_query.lower()
        filtered = []
        for product in PRODUCTS:
            if query not in " ".join(product).lower():
                continue
            if self.stock_filter == "Low" and product[6] != "Low":
                continue
            if self.stock_filter == "Near Expiry" and "expir" not in product[6].lower():
                continue
            if self.stock_filter == "Untracked" and product[6] != "Untracked":
                continue
            filtered.append((*product[:6], badge(product[6], product[7])))
        search = ft.TextField(
            hint_text="Search products or barcode",
            value=self.stock_query,
            on_change=lambda e: self.set_stock_query(e.control.value),
        )
        chips = ft.Row(
            [
                rounded_button(
                    option,
                    lambda _, value=option: self.set_stock_filter(value),
                    PALE_BLUE if self.stock_filter == option else PALE_LAVENDER,
                )
                for option in ["All", "Low", "Near Expiry", "Untracked"]
            ],
            wrap=True,
        )
        return ft.Column(
            [
                ft.Row([ft.Container(expand=True), rounded_button("+ Register Product", bgcolor=PALE_BLUE)]),
                search,
                chips,
                ft.GestureDetector(
                    content=card(self.data_table(["Barcode", "Name", "Category", "Units", "Cost", "Price", "Status"], filtered), padding=10),
                    on_tap=self.go("adjust"),
                ),
                ft.Column(
                    [
                        text("Every shelf, a little more organized.", 23, GREEN),
                        text("Find your products, check availability, and spot what needs attention.", 14, MUTED),
                    ]
                ),
            ],
            spacing=20,
        )

    def set_stock_query(self, value: str):
        self.stock_query = value
        self.render()

    def set_stock_filter(self, value: str):
        self.stock_filter = value
        self.render()

    def restock(self) -> ft.Control:
        rows = [
            ("92", "Sardines 155g", "1.5", "2.0 / day", "24", badge("Urgent", "red")),
            ("85", "Bottled water 500ml", "3", "16 / day", "60", badge("Urgent", "red")),
            ("61", "Pencil HB", "6", "1.0 / day", "12", badge("Soon", "amber")),
            ("48", "Instant noodles", "9", "6.5 / day", "40", badge("Soon", "amber")),
        ]
        return ft.Column(
            [
                ft.Row(
                    [
                        rounded_button("Priority Queue", bgcolor=PALE_BLUE),
                        rounded_button("Fast / Slow Movers", bgcolor=PALE_LAVENDER),
                    ],
                    wrap=True,
                ),
                card(self.data_table(["Score", "Product", "Days of cover", "14-day speed", "Suggested qty", "Urgency"], rows), padding=10),
                card(
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LOCAL_SHIPPING_OUTLINED, size=36, color=GREEN),
                            ft.Column(
                                [
                                    text("Keep your favorites on the shelf.", 21, GREEN),
                                    text("Start with urgent items, then work your way down the priority queue.", 14, MUTED),
                                ]
                            ),
                        ],
                        spacing=28,
                    ),
                    bgcolor=PALE_GREEN,
                    padding=30,
                ),
            ],
            spacing=26,
        )

    def reports(self) -> ft.Control:
        periods = ft.Row(
            [
                rounded_button(
                    option,
                    lambda _, value=option: self.set_report_period(value),
                    PALE_BLUE if self.report_period == option else PALE_LAVENDER,
                )
                for option in ["Day", "Week", "Month", "Custom"]
            ],
            wrap=True,
            alignment=ft.MainAxisAlignment.END,
        )
        stats = ft.ResponsiveRow(
            [
                ft.Container(stat_card("Revenue", "₱31,400.00"), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("Gross profit", "₱8,250.00", PALE_GREEN, "#1D6538"), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("Margin", "26.3%", PALE_YELLOW), col={"sm": 6, "lg": 3}),
                ft.Container(stat_card("COGS", "₱23,150.00", PALE_ROSE), col={"sm": 6, "lg": 3}),
            ],
            spacing=16,
            run_spacing=16,
        )
        values = [44, 62, 36, 72, 56, 88, 66]
        colors = ["#D9EACD", "#FFD7BF", "#FFF0C7", "#E7DAF4", "#D9EACD", GREEN, "#FFD7BF"]
        chart = ft.BarChart(
            bar_groups=[
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=value,
                            width=38,
                            color=colors[i],
                            border_radius=ft.border_radius.only(top_left=12, top_right=12),
                        )
                    ],
                )
                for i, value in enumerate(values)
            ],
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=i, label=text(day, 12, MUTED))
                    for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
                ]
            ),
            left_axis=ft.ChartAxis(labels_size=0),
            max_y=100,
            height=280,
            interactive=True,
        )
        links = ft.ResponsiveRow(
            [
                ft.Container(rounded_button(label, self.go("history") if i == 0 else None, PALE_LAVENDER), col={"sm": 6, "lg": 3})
                for i, label in enumerate(["Best and worst sellers ›", "Profit per item ›", "Spoilage loss ›", "Inventory value ›"])
            ],
            spacing=14,
            run_spacing=14,
        )
        return ft.Column([periods, stats, card(ft.Column([text("Sales and profit trend", 20, INK, ft.FontWeight.W_600), chart])), links], spacing=22)

    def set_report_period(self, value: str):
        self.report_period = value
        self.render()

    def sell_states(self) -> ft.Control:
        controls = [
            card(
                ft.Column(
                    [
                        ft.Row([ft.Icon(ft.Icons.SHOPPING_CART_OUTLINED, color=GREEN), text("Empty cart", color=MUTED)]),
                        text("Cart is empty. Scan a product to start.", weight=ft.FontWeight.W_600),
                        rounded_button("Checkout", disabled=True),
                    ],
                    spacing=18,
                ),
                height=245,
            ),
            card(
                ft.Column(
                    [
                        ft.Row([ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=GREEN), text("Not enough stock", color=MUTED)]),
                        text("Fresh Milk 1L × 5"),
                        text("Only 3 left. Lower the quantity.", color="#C70028", weight=ft.FontWeight.W_600),
                        ft.Row([ft.IconButton(ft.Icons.REMOVE), text("5"), ft.IconButton(ft.Icons.ADD)]),
                    ],
                    spacing=14,
                ),
                bgcolor="#FFF3DC",
                height=245,
            ),
            card(
                ft.Column(
                    [
                        ft.Row([ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=GREEN), text("Only expired stock left", color=MUTED)]),
                        text("Only expired stock left. It cannot be sold.", color="#C70028", weight=ft.FontWeight.W_600),
                        ft.TextButton("Go to write-off list"),
                    ],
                    spacing=16,
                ),
                bgcolor="#FBEAE4",
                height=200,
            ),
        ]
        return ft.ResponsiveRow(
            [ft.Container(control, col={"sm": 12, "md": 6}) for control in controls],
            spacing=22,
            run_spacing=22,
        )

    def adjust(self) -> ft.Control:
        status = ft.Text("", color=GREEN)

        def save(_):
            status.value = "Adjustment saved"
            status.update()

        form = card(
            ft.Column(
                [
                    ft.Dropdown(label="Batch", value="batch-a", options=[ft.dropdown.Option(key="batch-a", text="Batch A · exp 12 Nov 2026")]),
                    ft.TextField(label="Current count", value="8", read_only=True),
                    ft.TextField(label="New count (after physical check)", value="6"),
                    ft.TextField(label="Reason", value="Counted 6 on shelf"),
                    rounded_button("Save adjustment", save, PALE_BLUE),
                    status,
                    text("Saved with old count, new count and reason. History is never edited.", 12, MUTED),
                ],
                spacing=14,
            ),
            expand=True,
        )
        note = card(
            ft.Column(
                [
                    ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=38, color=GREEN),
                    text("A fresh count.", 21, GREEN),
                    text("Count what’s on your shelf,\nthen leave a reason to keep\nyour stock history clear.", 14, MUTED),
                ]
            ),
            bgcolor=PALE_GREEN,
            width=None if self.compact else 320,
        )
        controls = [ft.Row([ft.Container(expand=True), rounded_button("Cancel", self.go("stock"), PALE_LAVENDER)])]
        controls.append(ft.Column([form, note], spacing=20) if self.compact else ft.Row([form, note], spacing=24, vertical_alignment=ft.CrossAxisAlignment.START))
        return ft.Column(controls, spacing=18)

    def history(self) -> ft.Control:
        data = [
            ("7 Nov 10:42", "Sale", "3 items", "PHP 184.00", "green"),
            ("7 Nov 09:15", "Receive", "Fresh Milk 1L × 24", "PHP 1,152.00", "amber"),
            ("6 Nov 17:30", "Write-off", "Yogurt cup × 2", "PHP 70.00", "red"),
            ("6 Nov 12:05", "Sale", "2 items", "PHP 90.00", "green"),
        ]
        rows = []
        for index, row in enumerate(data):
            if self.history_filter != "All" and row[1] != self.history_filter:
                continue
            action = rounded_button("Void last sale", bgcolor=PALE_LAVENDER) if index == 0 and self.history_filter == "All" else text("")
            rows.append((row[0], badge(row[1], row[4]), row[2], row[3], action))
        filters = ft.Row(
            [
                rounded_button(
                    option,
                    lambda _, value=option: self.set_history_filter(value),
                    PALE_BLUE if self.history_filter == option else PALE_LAVENDER,
                )
                for option in ["All", "Sale", "Receive", "Void", "Adjustment", "Write-off"]
            ],
            wrap=True,
        )
        return ft.Column(
            [
                filters,
                card(self.data_table(["Date", "Type", "Details", "Amount", ""], rows), padding=10),
                text("Undo is available only on the latest transaction.", 13, MUTED),
            ],
            spacing=22,
        )

    def set_history_filter(self, value: str):
        self.history_filter = value
        self.render()

    @staticmethod
    def data_table(headers: list[str], rows) -> ft.Control:
        def cell(value):
            return ft.DataCell(value if isinstance(value, ft.Control) else text(str(value), 14))

        table = ft.DataTable(
            columns=[ft.DataColumn(text(header, 12, MUTED, ft.FontWeight.W_600)) for header in headers],
            rows=[ft.DataRow(cells=[cell(value) for value in row]) for row in rows],
            column_spacing=26,
            horizontal_lines=ft.BorderSide(1, "#EBE8E1"),
            heading_row_height=48,
            data_row_min_height=52,
        )
        return ft.Row([table], scroll=ft.ScrollMode.AUTO)


def main(page: ft.Page):
    StockFlow(page)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Use project assets directory
    root_assets = Path(__file__).resolve().parent.parent.parent / "assets"
    assets_path = str(root_assets) if root_assets.exists() else "assets"

    is_web = "--web" in sys.argv
    view_mode = ft.AppView.WEB_BROWSER if is_web else ft.AppView.FLET_APP
    port = 8550 if is_web else 0

    ft.app(target=main, assets_dir=assets_path, port=port, view=view_mode)
