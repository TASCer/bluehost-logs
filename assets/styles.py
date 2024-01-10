# TODO work on header format 
def get_style_changes():
	web_styles_changes = [
		dict(selector="th", props=[
			("color", "black"),
			("border", "1px solid #eee"),
			("padding", "6px 7px"),
			("background", "light-grey"),
			("font-size", "18px")
			]),

		dict(selector="td:nth-child(-n + 2)", props=[
			("color", "black"), 
			("font-size", "16px")
			]),

		dict(selector="tr", props=[
			("color", "red"), 
			("font-size", "15px")
			]),

		dict(selector=" ", props=[
			("font-family", "Arial"),
			("text-align", "center"),
			("margin", "12px auto"),
			("border", "6px solid black")
			]),

		dict(selector="caption", props=[
			("caption-side", "top"), 
			("font-size", "16px"), 
			("color", "blue")
			])
	]

	return web_styles_changes


def get_style_finance():
	web_styles_finance = [
		dict(selector="th", props=[
			("color", "black"),
			("border", "1px solid #eee"),
			("padding", "6px 7px"),
			("background", "light-grey"),
			("font-size", "18px")
			]),

		dict(selector="td:last-child", props=[
			("color", "green"), 
			("font-size", "18px")
			]),

		dict(selector=" ", props=[
			("font-family", "Roboto"),
			("text-align", "center"),
			("margin", "20px auto"),
			("border", "6px solid black"),
			("table-layout", "fixed"),
			("border-style", "ridge")
			]),

		dict(selector="caption", props=[
			("caption-side", "top"), 
			("font-size", "20px"), 
			("color", "blue")
			])

	]

	return web_styles_finance

# dict(selector="td:last-child", props=[("color", "#006400"),
# 	("text-align", "center"),
# 	("font-size", "15px")
# 	]),


# dict(selector="th:last-child", props=[("color", "red")]),
# dict(selector="td", props=[("text-align", "center"), ("font-size", "15px"), ('color', 'green')]),

# dict(selector="th:first-child", props=[("color", "red"),
# 	("margin", "2px auto"),
# 	("border-collapse", "collapse"),
# 	("border", "6px solid black"),
# ]),


# <table border="1" cellpadding="5" cellspacing="0" style="background-color: #F0F5FF; border-style: ridge; color: #4040C0" width="100%">