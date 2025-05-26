import os
import psutil
import socket
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN = "7891024666:AAEAmgg2RVeLGh4PurF7byANFKXW-904_08"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   await update.message.reply_text(
        "🖥️ <b>Системный монитор Alt Linux</b> 🖥️\n\n"
        "Доступные команды:\n"
        "/status - Краткая сводка системы\n"
        "/fullstatus - Полная информация о системе\n"
        "/processes - Топ процессов по CPU/RAM\n"
        "/disks - Информация о дисках\n"
        "/network - Сетевая статистика\n\n"
        "Или просто напишите 'статус'",
        parse_mode='HTML'
    )

def get_short_status():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    
    return (
        f"📊 <b>Краткий статус системы</b>\n\n"
        f"🖥 CPU: {cpu}%\n"
        f"🧠 RAM: {mem.percent}% ({mem.used/1024**3:.1f}GB/{mem.total/1024**3:.1f}GB)\n"
        f"💾 Диск: {disk.percent}% ({disk.used/1024**3:.1f}GB/{disk.total/1024**3:.1f}GB)\n"
        f"⏱ Время работы: {datetime.now() - boot_time}\n"
    )

def get_full_status():
    # CPU информация
    cpu_info = psutil.cpu_freq()
    cpu_cores = f"{psutil.cpu_count(logical=False)} ядер, {psutil.cpu_count(logical=True)} потоков"
    
    # Память
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Диски
    disks = []
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        disks.append(
            f"📌 {part.device} ({part.fstype}) -> {part.mountpoint}\n"
            f"   Использовано: {usage.percent}% ({usage.used/1024**3:.1f}GB/{usage.total/1024**3:.1f}GB)"
        )
    
    # Температура
    try:
        temps = psutil.sensors_temperatures()
        temp_info = "\n".join([f"🌡 {name}: {current}°C" for name, current in temps.get('coretemp', [])])
    except:
        temp_info = "Температура: данные недоступны"
    
    # Сеть
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    net_io = psutil.net_io_counters()
    
    return (
        f"🔍 <b>Полная информация о системе</b>\n\n"
        f"<b>Процессор:</b>\n"
        f"Использование: {psutil.cpu_percent(interval=1)}%\n"
        f"Частота: {cpu_info.current:.0f}MHz (макс: {cpu_info.max:.0f}MHz)\n"
        f"Архитектура: {cpu_cores}\n\n"
        
        f"<b>Память:</b>\n"
        f"ОЗУ: {mem.percent}% ({mem.used/1024**3:.1f}GB/{mem.total/1024**3:.1f}GB)\n"
        f"Swap: {swap.percent}% ({swap.used/1024**3:.1f}GB/{swap.total/1024**3:.1f}GB)\n\n"
        
        f"<b>Диски:</b>\n" + "\n".join(disks) + "\n\n"
        
        f"<b>Температура:</b>\n{temp_info}\n\n"
        
        f"<b>Сеть:</b>\n"
        f"Хост: {hostname}\n"
        f"IP: {ip_address}\n"
        f"Отправлено: {net_io.bytes_sent/1024**2:.1f}MB\n"
        f"Получено: {net_io.bytes_recv/1024**2:.1f}MB\n\n"
        
        f"<b>Система:</b>\n"
        f"Загрузка: {os.getloadavg()}\n"
        f"Время работы: {datetime.now() - datetime.fromtimestamp(psutil.boot_time())}"
    )

def get_top_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except:
            continue
    
    top_cpu = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:5]
    top_mem = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)[:5]
    
    cpu_info = "\n".join([f"{p['name']}: {p['cpu_percent']}%" for p in top_cpu])
    mem_info = "\n".join([f"{p['name']}: {p['memory_percent']}%" for p in top_mem])
    
    return (
        f"🏆 <b>Топ процессов</b>\n\n"
        f"<b>По CPU:</b>\n{cpu_info}\n\n"
        f"<b>По памяти:</b>\n{mem_info}"
    )

def get_disk_info():
    result = ["💽 <b>Информация о дисках</b>\n"]
    for part in psutil.disk_partitions(all=False):
        usage = psutil.disk_usage(part.mountpoint)
        result.append(
            f"\n📌 <b>{part.device}</b> ({part.fstype})\n"
            f"Точка монтирования: {part.mountpoint}\n"
            f"Использовано: {usage.percent}% ({usage.used/1024**3:.1f}GB/{usage.total/1024**3:.1f}GB)\n"
            f"Свободно: {usage.free/1024**3:.1f}GB"
        )
    return "\n".join(result)

def get_network_info():
    net_io = psutil.net_io_counters()
    net_if = psutil.net_if_addrs()
    
    interfaces = []
    for name, addrs in net_if.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                interfaces.append(f"🔹 {name}: {addr.address}")
    
    return (
        f"🌐 <b>Сетевая статистика</b>\n\n"
        f"<b>Интерфейсы:</b>\n" + "\n".join(interfaces) + "\n\n"
        f"<b>Трафик:</b>\n"
        f"Отправлено: {net_io.bytes_sent/1024**2:.1f}MB\n"
        f"Получено: {net_io.bytes_recv/1024**2:.1f}MB\n"
        f"Пакеты отправлено: {net_io.packets_sent}\n"
        f"Пакеты получено: {net_io.packets_recv}"
    )

# Обработчики команд
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_short_status(), parse_mode='HTML')

async def fullstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_full_status(), parse_mode='HTML')

async def processes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_top_processes(), parse_mode='HTML')

async def disks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_disk_info(), parse_mode='HTML')

async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_network_info(), parse_mode='HTML')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text in ['статус', 'status']:
        await status(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("fullstatus", fullstatus))
    app.add_handler(CommandHandler("processes", processes))
    app.add_handler(CommandHandler("disks", disks))
    app.add_handler(CommandHandler("network", network))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()
