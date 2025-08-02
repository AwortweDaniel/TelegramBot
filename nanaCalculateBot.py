from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import ast
import operator
import math

from dotenv import load_dotenv
import os


load_dotenv(dotenv_path=".env.local")

TOKEN = os.getenv("BOT_TOKEN")

# Supported operators & functions
OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}

# math functions
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

# Safe Evaluator


def safe_eval(expr):
    try:
        node = ast.parse(expr, mode='eval').body
        return eval_node(node)
    except Exception:
        return "An Error occured: Invalid expression\n`/help` - Show this help message\n"


def eval_node(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        return OPERATORS[type(node.op)](eval_node(node.left), eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        return OPERATORS[type(node.op)](eval_node(node.operand))
    elif isinstance(node, ast.Call):
        func_name = node.func.id
        if func_name in ALLOWED_FUNCTIONS:
            args = [eval_node(arg) for arg in node.args]
            return ALLOWED_FUNCTIONS[func_name](*args)
        else:
            raise ValueError("Unsupported function\n`/help` - Show this help message\n")
    elif isinstance(node, ast.Name):
        if node.id in ALLOWED_FUNCTIONS:
            return ALLOWED_FUNCTIONS[node.id]
        else:
            raise ValueError("Unknown constant\n`/help` - Show this help message\n")
    else:
        raise ValueError("Unsupported expression\n`/help` - Show this help message\n")

# Bot Handlers

# /start command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I’m nanaCalculate, your Math Bot.\nAnything calculation "
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

# Run Bot


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