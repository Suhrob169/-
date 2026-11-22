"""
PARVINA CAKES — мобильное приложение.
Запуск: python parvina_app_v2.py
"""
import os, json, math, time, urllib.parse, urllib.request
import flet as ft
import flet.canvas as cv

# ═══ НАСТРОЙКИ ═══════════════════════════════════════════════════════
SHOP = "PARVINA CAKES"
PHONE = "+992 98 333 6184"
WHATSAPP = "992983336184"
ADDRESS = "Худжанд, ул. Мирзосангин Рустамова 81/4"
HOURS = "Ежедневно 24/7"
FREE_FROM, FEE = 200, 20

# ⚠️ ВАЖНО: Когда загрузите server.py на Render, замените эту ссылку!
SERVER_API = "SERVER_API = "https://parvinacakes02.fly.dev/api/order"" 

PRODUCTS = [
    ("Медовик", "Нежный торт с медовыми коржами и сметанным кремом", 120, 140, "шт.", "Торты", "🎂", "medovik.jpg"),
    ("Макаронс", "Ассорти: фисташка, малина, шоколад", 15, None, "шт.", "Печенье", "🍪", "macarons.jpg"),
    ("Эклер", "Заварное тесто, ванильный крем, глазурь", 12, None, "шт.", "Пирожные", "🥐", "ekler.jpg"),
]
# ═════════════════════════════════════════════════════════════════════

RASP, COCOA, PAPER, BLUSH, PIST, GOLD, LINE, MUTED = (
    "#8e1b47", "#2b161d", "#fff8f3", "#fbe9ea", "#cfe3c1", "#f0b44c", "#efd5d8", "#7a6168")
TILES = [[PIST, "#ffd6c2"], ["#ffd6c2", "#fbe0e6"], ["#fbe0e6", "#e6d7f5"], ["#fff0c9", PIST]]
BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
os.makedirs(ASSETS, exist_ok=True)
W = ft.FontWeight
CENTER = ft.alignment.center
FONT_P = "https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf"
FONT_M = "https://raw.githubusercontent.com/google/fonts/main/ofl/manrope/Manrope%5Bwght%5D.ttf"

def T(s, size=14, w=W.W_600, color=COCOA, **kw):
    return ft.Text(s, size=size, weight=w, color=color, **kw)

def H(s, size=24, color=COCOA, **kw):
    return T(s, size, W.W_800, color, font_family="Playfair", **kw)

def money(n):
    return f"{n:g} сом."

def fmt_phone(d):
    return f"+992 {d[:2]} {d[2:5]} {d[5:]}".strip()

def fan(size, c1, c2, hub):
    s = size / 120
    base = [(60, 60), (48, 40), (52, 14), (60, 10), (68, 14), (72, 40), (60, 60)]
    shapes = []
    for i in range(6):
        a = math.radians(i * 60)
        ca, sa = math.cos(a), math.sin(a)
        p = [((60 + (x - 60) * ca - (y - 60) * sa) * s, (60 + (x - 60) * sa + (y - 60) * ca) * s) for x, y in base]
        shapes.append(cv.Path([cv.Path.MoveTo(*p[0]), cv.Path.CubicTo(*p[1], *p[2], *p[3]),
                               cv.Path.CubicTo(*p[4], *p[5], *p[6]), cv.Path.Close()],
                              paint=ft.Paint(color=c1 if i % 2 == 0 else c2, style=ft.PaintingStyle.FILL)))
    shapes += [cv.Circle(60 * s, 60 * s, 11 * s, ft.Paint(color=hub)), cv.Circle(60 * s, 60 * s, 4 * s, ft.Paint(color=c2))]
    return cv.Canvas(shapes, width=size, height=size)


def main(page: ft.Page):
    page.title = SHOP
    page.bgcolor = PAPER
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.fonts = {"Playfair": FONT_P, "Manrope": FONT_M}
    page.theme = ft.Theme(font_family="Manrope", color_scheme_seed=RASP)
    
    try:
        page.window.width, page.window.height = 390, 844
    except:
        pass

    store = page.client_storage
    cart = {}
    st = {"cat": "Все", "q": "", "mode": "pickup", "addr": "", "tab": 0}
    user = {}
    try:
        fav = set(json.loads(store.get("fav") or "[]"))
    except Exception:
        fav = set()

    def open_dlg(d): page.open(d)
    def close_dlg(d): page.close(d)
    def toast(t): page.open(ft.SnackBar(ft.Text(t), bgcolor=COCOA, behavior=ft.SnackBarBehavior.FLOATING))
    def total(): return sum(PRODUCTS[i][2] * q for i, q in cart.items())

    def thumb(i, size):
        p = PRODUCTS[i]
        has = p[7] and os.path.exists(os.path.join(ASSETS, p[7]))
        return ft.Container(
            ft.Image(src=p[7], width=size, height=size, fit=ft.ImageFit.COVER) if has else T(p[6], size * .5),
            width=size, height=size, alignment=CENTER, border_radius=size * .28, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, colors=TILES[i % 4]))

    def btn(text, on_click, bg=RASP, fg="white", h=54):
        return ft.ElevatedButton(content=T(text, 16, W.W_800, fg), on_click=on_click, height=h,
                                 style=ft.ButtonStyle(bgcolor=bg, shape=ft.RoundedRectangleBorder(radius=18), elevation=0))

    def field(label, icon, **kw):
        return ft.TextField(label=label, prefix_icon=icon, filled=True, fill_color="white", border_radius=16,
                            border_color=LINE, focused_border_color=RASP, cursor_color=RASP, color=COCOA,
                            label_style=ft.TextStyle(color=MUTED), content_padding=ft.padding.symmetric(16, 18), **kw)

    def shadow():
        return ft.BoxShadow(blur_radius=18, offset=ft.Offset(0, 6), color=ft.Colors.with_opacity(0.10, COCOA))

    def splash():
        page.clean()
        page.navigation_bar = None
        page.bgcolor = PAPER
        ease = ft.AnimationCurve.EASE_OUT_CUBIC
        logo = ft.Container(fan(190, RASP, GOLD, COCOA), width=190, height=190,
                            rotate=ft.Rotate(-6 * math.pi, alignment=CENTER), scale=0.15, opacity=0,
                            animate_rotation=ft.Animation(2800, ease), animate_scale=ft.Animation(2800, ease),
                            animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_IN))
        word = ft.Container(
            ft.Column([H("PARVINA", 36, RASP, style=ft.TextStyle(letter_spacing=5)),
                       ft.Row([ft.Container(width=34, height=2, bgcolor=GOLD),
                               T("CAKES", 14, W.W_800, COCOA, style=ft.TextStyle(letter_spacing=8)),
                               ft.Container(width=34, height=2, bgcolor=GOLD)],
                              alignment=ft.MainAxisAlignment.CENTER)],
                      horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
            opacity=0, offset=ft.Offset(0, 0.3),
            animate_opacity=ft.Animation(1000, ease), animate_offset=ft.Animation(1000, ease))
        screen = ft.Container(ft.Column([logo, word], alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=28),
                              expand=True, alignment=CENTER, animate_opacity=ft.Animation(500, ease))
        page.add(screen)
        page.update()
        time.sleep(0.3)
        logo.rotate, logo.scale, logo.opacity = ft.Rotate(0, alignment=CENTER), 1, 1
        page.update()
        time.sleep(1.5)
        word.opacity, word.offset = 1, ft.Offset(0, 0)
        page.update()
        time.sleep(2.0)
        screen.opacity = 0
        page.update()
        time.sleep(0.5)

    def register(edit=False):
        page.clean()
        page.navigation_bar = None
        page.bgcolor = RASP
        name = field("Ваше имя", ft.Icons.PERSON_OUTLINE, value=user.get("name", ""), capitalization=ft.TextCapitalization.WORDS)
        digits = "".join(c for c in user.get("phone", "")[4:] if c.isdigit())
        phone = field("Номер телефона", ft.Icons.PHONE_OUTLINED, value=digits, prefix_text="+992 ", max_length=9,
                      counter_text=" ", keyboard_type=ft.KeyboardType.PHONE, input_filter=ft.NumbersOnlyInputFilter())
        where = field("Откуда вы? (город, район)", ft.Icons.LOCATION_ON_OUTLINED, value=user.get("where", ""),
                      capitalization=ft.TextCapitalization.WORDS)

        def submit(e):
            n, d, w = name.value.strip(), "".join(c for c in phone.value if c.isdigit()), where.value.strip()
            name.error_text = "Введите имя" if len(n) < 2 else None
            phone.error_text = "Введите 9 цифр номера" if len(d) < 9 else None
            where.error_text = "Укажите, откуда вы" if len(w) < 2 else None
            if name.error_text or phone.error_text or where.error_text:
                return page.update()
            user.update(name=n, phone=fmt_phone(d), where=w)
            store.set("user", json.dumps(user, ensure_ascii=False))
            st["addr"] = ""
            open_app()

        ease = ft.AnimationCurve.EASE_OUT_CUBIC
        sheet = ft.Container(
            ft.Column([
                H("Давайте познакомимся" if not edit else "Ваши данные", 26),
                T("Эти данные нужны, чтобы мы подтвердили заказ и доставили сладости.", 13, W.W_500, MUTED),
                ft.Container(height=2), name, phone, where, ft.Container(height=2),
                btn("Войти" if not edit else "Сохранить", submit),
                ft.Row([T("🔒 Данные хранятся только на вашем телефоне", 11, W.W_500, MUTED)], alignment=ft.MainAxisAlignment.CENTER),
            ], spacing=14, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
            bgcolor=PAPER, expand=True, padding=ft.padding.only(24, 28, 24, 20),
            border_radius=ft.border_radius.only(top_left=36, top_right=36),
            offset=ft.Offset(0, 0.15), opacity=0, animate_offset=ft.Animation(650, ease), animate_opacity=ft.Animation(500, ease))
        top = ft.Container(ft.Column([fan(78, PAPER, GOLD, COCOA), H(SHOP, 22, PAPER),
                                      T("Добро пожаловать!" if not edit else "Профиль", 13, W.W_600, GOLD)],
                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                           padding=ft.padding.only(top=26, bottom=26), alignment=CENTER)
        page.add(ft.SafeArea(ft.Column([top, sheet], spacing=0, expand=True), expand=True))
        page.update()
        time.sleep(0.1)
        sheet.offset, sheet.opacity = ft.Offset(0, 0), 1
        page.update()

    def open_app():
        page.clean()
        page.bgcolor = PAPER
        refs = {}

        def nav_destinations():
            n = sum(cart.values())
            return [
                ft.NavigationBarDestination(icon=ft.Icons.STOREFRONT_OUTLINED, selected_icon=ft.Icons.STOREFRONT, label="Меню"),
                ft.NavigationBarDestination(icon=ft.Icons.FAVORITE_BORDER, selected_icon=ft.Icons.FAVORITE, label="Избранное"),
                ft.NavigationBarDestination(icon=ft.Icons.SHOPPING_BAG_OUTLINED, selected_icon=ft.Icons.SHOPPING_BAG,
                                            label=f"Коробка ({n})" if n else "Коробка"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, selected_icon=ft.Icons.PERSON, label="Профиль"),
            ]

        body = ft.Container(expand=True, animate_opacity=ft.Animation(160, ft.AnimationCurve.EASE_IN_OUT))
        nav = ft.NavigationBar(destinations=nav_destinations(), selected_index=0, bgcolor="white",
                               indicator_color=BLUSH, on_change=lambda e: go(e.control.selected_index))
        page.navigation_bar = nav

        def sync_nav(): nav.destinations = nav_destinations()

        def paint(i):
            r = refs.get(i)
            if not r: return
            q = cart.get(i, 0)
            r["plus"].visible, r["step"].visible = q == 0, q > 0
            r["qty"].value = str(q)

        def bump(i, d, rebuild=False):
            cart[i] = cart.get(i, 0) + d
            if cart[i] < 1: cart.pop(i)
            paint(i)
            sync_nav()
            if rebuild: body.content = cart_view()
            page.update()

        def toggle_fav(i):
            fav.symmetric_difference_update({i})
            store.set("fav", json.dumps(sorted(fav)))
            r = refs.get(i)
            if r: r["heart"].icon = ft.Icons.FAVORITE if i in fav else ft.Icons.FAVORITE_BORDER
            if st["tab"] == 1: body.content = fav_view()
            page.update()

        def pcard(i):
            n, desc, price, old, unit, cat, emoji, img = PRODUCTS[i]
            q = cart.get(i, 0)
            heart = ft.IconButton(ft.Icons.FAVORITE if i in fav else ft.Icons.FAVORITE_BORDER, icon_color=RASP,
                                  icon_size=18, bgcolor=ft.Colors.with_opacity(.85, "white"), on_click=lambda e: toggle_fav(i))
            plus = ft.Container(T("+", 22, W.W_800, "white"), width=38, height=38, border_radius=19, bgcolor=COCOA,
                                alignment=CENTER, ink=True, visible=q == 0, on_click=lambda e: bump(i, 1))
            qty = T(str(q), 14, W.W_800, COCOA)
            step = ft.Container(ft.Row([
                ft.Container(T("−", 18, W.W_800, COCOA), width=28, height=34, alignment=CENTER, ink=True, on_click=lambda e: bump(i, -1)),
                qty,
                ft.Container(T("+", 18, W.W_800, COCOA), width=28, height=34, alignment=CENTER, ink=True, on_click=lambda e: bump(i, 1)),
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER), bgcolor=GOLD, border_radius=19, visible=q > 0)
            refs[i] = dict(plus=plus, step=step, qty=qty, heart=heart)
            tag = (ft.Container(T(f"-{round((1 - price / old) * 100)}%", 11, W.W_800, "white"), bgcolor=RASP,
                                border_radius=10, padding=ft.padding.symmetric(6, 3), left=8, top=10) if old else ft.Container())
            tile = ft.Container(ft.Stack([ft.Container(thumb(i, 118), alignment=CENTER, expand=True), tag,
                                          ft.Container(heart, right=2, top=2)]), height=118)
            return ft.Container(
                ft.Column([tile, T(n, 16, W.W_800, COCOA, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                           T(desc, 11, W.W_500, MUTED, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                           ft.Row([ft.Column([T(money(price), 15, W.W_800, RASP),
                                              T(f"{money(old)}" if old else f"за {unit}", 10, W.W_500, MUTED,
                                                style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH) if old else None)],
                                             spacing=0, expand=True), ft.Stack([plus, step], width=92, height=38)],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.END)],
                          spacing=6),
            bgcolor="white", border_radius=24, padding=10, shadow=shadow())

        def grid(indices):
            refs.clear()
            g = ft.GridView(expand=True, runs_count=2, child_aspect_ratio=0.62, spacing=12, run_spacing=12,
                            padding=ft.padding.only(16, 8, 16, 16))
            g.controls = [pcard(i) for i in indices]
            return g

        def title_bar(text, sub=""):
            return ft.Container(ft.Column([H(text, 28, PAPER), T(sub, 12, W.W_500, GOLD) if sub else ft.Container()], spacing=2),
                                bgcolor=RASP, padding=ft.padding.only(20, 16, 20, 20),
                                border_radius=ft.border_radius.only(bottom_left=32, bottom_right=32))

        def menu_view():
            cats = ["Все"] + sorted({p[5] for p in PRODUCTS})
            holder = ft.Container(expand=True)
            chips = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)

            def match(i):
                p = PRODUCTS[i]
                return (st["cat"] == "Все" or p[5] == st["cat"]) and st["q"] in (p[0] + " " + p[1]).lower()

            def fill():
                chips.controls = [ft.Container(T(c, 13, W.W_700, "white" if c == st["cat"] else COCOA),
                                               padding=ft.padding.symmetric(16, 9), border_radius=20, ink=True,
                                               bgcolor=COCOA if c == st["cat"] else "white", border=ft.border.all(1, LINE),
                                               on_click=lambda e, c=c: (st.update(cat=c), fill(), page.update()))
                                  for c in cats]
                idx = [i for i in range(len(PRODUCTS)) if match(i)]
                holder.content = grid(idx) if idx else ft.Container(T("Ничего не нашли 🙈", 14, W.W_600, MUTED), alignment=CENTER)

            def on_search(e):
                st["q"] = (e.control.value or "").lower().strip()
                fill()
                page.update()

            search = ft.TextField(hint_text="Найти торт, эклер…", prefix_icon=ft.Icons.SEARCH, filled=True, fill_color="white",
                                  border_radius=18, border_color="transparent", height=48, text_size=14, color=COCOA,
                                  content_padding=ft.padding.symmetric(10, 12), on_change=on_search, value=st["q"])
            header = ft.Container(ft.Column([
                ft.Row([ft.Column([T("Здравствуйте,", 12, W.W_500, ft.Colors.with_opacity(.8, PAPER)), H(user["name"], 22, PAPER, max_lines=1)],
                                  spacing=0, expand=True), fan(44, PAPER, GOLD, COCOA)]),
                ft.Row([T("📍", 12), T(user["where"], 12, W.W_600, GOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)], spacing=4),
                search], spacing=10),
                bgcolor=RASP, padding=ft.padding.only(20, 14, 20, 18),
                border_radius=ft.border_radius.only(bottom_left=32, bottom_right=32))
            fill()
            return ft.Column([header, ft.Container(chips, padding=ft.padding.only(16, 14, 16, 0)), holder], spacing=0, expand=True)

        def fav_view():
            idx = [i for i in sorted(fav) if i < len(PRODUCTS)]
            inner = grid(idx) if idx else ft.Container(
                ft.Column([T("♥", 54, color=LINE), T("Здесь будут ваши любимые сладости", 14, W.W_600, MUTED)],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER), alignment=CENTER, expand=True)
            return ft.Column([title_bar("Избранное", f"{len(idx)} шт."), ft.Container(inner, expand=True)], spacing=0, expand=True)

        def cart_view():
            if not cart:
                return ft.Column([title_bar("Моя коробка"), ft.Container(ft.Column([
                    T("🧺", 64), T("Коробка пуста", 18, W.W_800), T("Добавьте что-нибудь вкусное", 13, W.W_500, MUTED),
                    ft.Container(height=8), btn("Выбрать сладости", lambda e: go(0))],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER), alignment=CENTER, expand=True)],
                    spacing=0, expand=True)
            s = total()
            deliv = st["mode"] == "delivery"
            fee = FEE if deliv and s < FREE_FROM else 0
            rows = [ft.Container(ft.Row([
                thumb(i, 56),
                ft.Column([T(PRODUCTS[i][0], 15, W.W_800, max_lines=1), T(f"{money(PRODUCTS[i][2])} × {q}", 12, W.W_500, MUTED),
                           T(money(PRODUCTS[i][2] * q), 14, W.W_800, RASP)], spacing=1, expand=True),
                ft.Container(ft.Row([
                    ft.Container(T("−", 18, W.W_800), width=30, height=34, alignment=CENTER, ink=True, on_click=lambda e, i=i: bump(i, -1, True)),
                    T(str(q), 14, W.W_800),
                    ft.Container(T("+", 18, W.W_800), width=30, height=34, alignment=CENTER, ink=True, on_click=lambda e, i=i: bump(i, 1, True))],
                    spacing=0), bgcolor=BLUSH, border_radius=18)], spacing=12),
                bgcolor="white", border_radius=20, padding=10, shadow=shadow()) for i, q in cart.items()]

            def set_mode(e):
                st["mode"] = next(iter(e.control.selected))
                body.content = cart_view()
                page.update()

            mode = ft.SegmentedButton(selected={st["mode"]}, on_change=set_mode, show_selected_icon=False,
                                      segments=[ft.Segment("pickup", label=T("Самовывоз", 13)), ft.Segment("delivery", label=T("Доставка", 13))])
            addr = field("Адрес доставки", ft.Icons.HOME_OUTLINED, value=st["addr"] or user["where"], visible=deliv,
                         on_change=lambda e: st.update(addr=e.control.value))
            left = FREE_FROM - s
            promo = ft.Column([T("🎉 Доставка бесплатная" if left <= 0 else f"До бесплатной доставки: {money(left)}", 12, W.W_700, MUTED),
                               ft.ProgressBar(value=min(1, s / FREE_FROM), color=GOLD, bgcolor=PIST, height=8, border_radius=4)],
                              spacing=6, visible=deliv)

            def order(e):
                where = f"Доставка: {st['addr'] or user['where']}" if deliv else "Самовывоз"
                
                cart_data = []
                for i, q in cart.items():
                    cart_data.append({"id": i, "name": PRODUCTS[i][0], "price": PRODUCTS[i][2], "qty": q})
                
                payload = json.dumps({
                    "cart": cart_data,
                    "name": user['name'],
                    "phone": user['phone'],
                    "address": where
                }).encode('utf-8')

                req = urllib.request.Request(SERVER_API, data=payload, headers={'Content-Type': 'application/json'})
                
                try:
                    with urllib.request.urlopen(req) as response:
                        res_data = json.loads(response.read().decode())
                        
                    if res_data.get("ok"):
                        oid = res_data['id']
                        cart.clear()
                        sync_nav()

                        if deliv:
                            info_text = f"Курьер привезёт заказ по адресу:\n{st['addr'] or user['where']}\nВ течение 1-2 часов."
                        else:
                            info_text = f"Ждём вас по адресу:\n{ADDRESS}\nЧасы работы: {HOURS}\nНазовите номер заказа при получении."

                        dlg = ft.AlertDialog(
                            shape=ft.RoundedRectangleBorder(radius=28),
                            content=ft.Column([
                                ft.Container(ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=64), alignment=CENTER),
                                H(f"Заказ №{oid} принят!", 24, COCOA, text_align=ft.TextAlign.CENTER),
                                T(info_text, 14, W.W_600, RASP, text_align=ft.TextAlign.CENTER),
                                ft.Container(height=10),
                                T("Если у вас есть вопросы, свяжитесь с нами:", 12, W.W_500, MUTED, text_align=ft.TextAlign.CENTER),
                                ft.Row([
                                    ft.ElevatedButton("Позвонить", icon=ft.Icons.PHONE, bgcolor=BLUSH, color=COCOA,
                                                      on_click=lambda e: page.launch_url("tel:" + PHONE.replace(" ", ""))),
                                    ft.ElevatedButton("WhatsApp", icon=ft.Icons.CHAT, bgcolor=PIST, color=COCOA,
                                                      on_click=lambda e: page.launch_url("https://wa.me/" + WHATSAPP))
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
                            ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                            actions=[
                                ft.TextButton("Вернуться в меню", on_click=lambda e: (close_dlg(dlg), go(0)), style=ft.ButtonStyle(color=RASP))
                            ],
                            actions_alignment=ft.MainAxisAlignment.CENTER
                        )
                        open_dlg(dlg)
                    else:
                        toast("Ошибка: " + res_data.get("error", "Неизвестно"))
                except Exception as ex:
                    print("Ошибка:", ex)
                    toast("Нет связи с сервером. Проверьте интернет.")

            summary = ft.Container(ft.Column([
                ft.Row([T("Сумма"), T(money(s))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([T("Доставка"), T("бесплатно" if not fee and deliv else money(fee) if deliv else "—")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color=LINE, height=8),
                ft.Row([H("Итого", 20), H(money(s + fee), 22, RASP)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                btn("Оформить заказ", order)], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                bgcolor="white", border_radius=24, padding=16, shadow=shadow())
            lst = ft.Column([*rows, ft.Container(height=4), mode, addr, promo, summary, ft.Container(height=12)],
                            spacing=12, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
            return ft.Column([title_bar("Моя коробка", f"{sum(cart.values())} шт. · {user['name']}, {user['phone']}"),
                              ft.Container(lst, padding=ft.padding.symmetric(16, 14), expand=True)], spacing=0, expand=True)

        def profile_view():
            def row(icon, text, sub, on=None):
                return ft.Container(ft.Row([ft.Container(ft.Icon(icon, color=RASP, size=22), width=44, height=44, bgcolor=BLUSH,
                                                         border_radius=14, alignment=CENTER),
                                            ft.Column([T(text, 14, W.W_700), T(sub, 12, W.W_500, MUTED)], spacing=0, expand=True),
                                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=LINE) if on else ft.Container()], spacing=12),
                                    bgcolor="white", border_radius=20, padding=12, ink=bool(on), on_click=on, shadow=shadow())

            def logout(e):
                store.remove("user")
                cart.clear()
                user.clear()
                register()

            def edit(e): register(edit=True)

            avatar = ft.Container(H(user["name"][:1].upper(), 34, PAPER), width=84, height=84, border_radius=42, bgcolor=RASP,
                                  alignment=CENTER, border=ft.border.all(4, GOLD))
            return ft.Column([
                ft.Container(ft.Column([avatar, H(user["name"], 22), T(user["phone"], 13, W.W_600, MUTED), T(f"📍 {user['where']}", 12, W.W_500, MUTED)],
                                       horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                             padding=ft.padding.only(top=24, bottom=14), alignment=CENTER),
                ft.Container(ft.Column([
                    row(ft.Icons.EDIT_OUTLINED, "Изменить данные", "Имя, телефон, откуда", edit),
                    row(ft.Icons.PHONE_OUTLINED, "Позвонить нам", PHONE, lambda e: page.launch_url("tel:" + PHONE.replace(" ", ""))),
                    row(ft.Icons.CHAT_OUTLINED, "Написать в WhatsApp", "Ответим быстро", lambda e: page.launch_url("https://wa.me/" + WHATSAPP)),
                    row(ft.Icons.LOCATION_ON_OUTLINED, "Мы находимся", f"{ADDRESS}\n{HOURS}"),
                    row(ft.Icons.LOGOUT, "Выйти", "Сменить пользователя", logout)],
                    spacing=10, scroll=ft.ScrollMode.AUTO), padding=ft.padding.symmetric(16, 0), expand=True)], spacing=0, expand=True)

        def go(t):
            st["tab"] = t
            nav.selected_index = t
            body.opacity = 0
            page.update()
            time.sleep(0.12)
            body.content = [menu_view, fav_view, cart_view, profile_view][t]()
            body.opacity = 1
            page.update()

        body.content = menu_view()
        page.add(ft.SafeArea(body, expand=True, bottom=False))
        page.update()

    splash()
    try:
        saved = json.loads(store.get("user") or "null")
    except Exception:
        saved = None
    if saved:
        user.update(saved)
        open_app()
    else:
        register()

if __name__ == "__main__":
    ft.app(target=main, assets_dir=ASSETS)
