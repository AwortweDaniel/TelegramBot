from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import ast
import operator
import math

# Replace with your real bot token
TOKEN = "7589042582:AAF91wT1o4-wk572u92DsUlau4ZcQ0xTb4k"

# Supported operators and functions
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

# Allowed math functions
ALLOWED_FUNCTIONS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'abs': abs,
    'round': round,
    'ceil': math.ceil,
    'floor': math.floor,
    'pi': math.pi,
    'e': math.e,
}

# ========== Safe Evaluator ==========


def safe_eval(expr):
    try:
        node = ast.parse(expr, mode='eval').body
        return eval_node(node)
    except Exception:
        return "An Error occured: Invalid expression"


def eval_node(node):
    if isinstance(node, ast.Num):  # 3, 4.5
        return node.n
    elif isinstance(node, ast.Constant):  # For Python 3.8+
        return node.value
    elif isinstance(node, ast.BinOp):  # a + b
        return OPERATORS[type(node.op)](eval_node(node.left), eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):  # -a
        return OPERATORS[type(node.op)](eval_node(node.operand))
    elif isinstance(node, ast.Call):  # function like sin(30)
        func_name = node.func.id
        if func_name in ALLOWED_FUNCTIONS:
            args = [eval_node(arg) for arg in node.args]
            return ALLOWED_FUNCTIONS[func_name](*args)
        else:
            raise ValueError("Unsupported function")
    elif isinstance(node, ast.Name):  # e, pi
        if node.id in ALLOWED_FUNCTIONS:
            return ALLOWED_FUNCTIONS[node.id]
        else:
            raise ValueError("Unknown constant")
    else:
        raise ValueError("Unsupported expression")

# ========== Bot Handlers ==========

# /start command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I’m your Math Bot."
        "\nSend any math expression like `2+3*sqrt(4)` and I’ll calculate it.\nUse /help to learn more."
    )

# /help command


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        " *nanaCalculate_bot Helpdesk*\n\n"
        "- Enter math expressions like:\n"
        "  `2 + 3 * (4 - 1)`\n"
        "  `sqrt(16) + sin(0)`\n\n"
        "- Supported functions:\n"
        "  `sqrt`, `sin`, `cos`, `tan`, `log`, `exp`, `abs`, `round`, `pi`, `e`\n\n"
        "- Commands:\n"
        "  `/start` - Welcome message\n"
        "  `/help` - Show this help message\n"
        "  `/clear` - Reset (placeholder)\n",
        parse_mode="Markdown"
    )

# /clear command


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cleared session ✅ \n(Note: I'm stateless for now).")

# Evaluate math input


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expr = update.message.text
    result = safe_eval(expr)
    await update.message.reply_text(f"Calculated result: `{result}`", parse_mode="Markdown")

# ========== Run Bot ==========


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))

    print("✅ Nana Calculate Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()