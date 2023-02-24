import telebot
from telebot import types
import random
import datetime


Token = '5973917345:AAFh1Uta4Y-mJXQJ2Ax-SrHDyssJTnmD9dU'

bot = telebot.TeleBot(Token)

class Task:
    def __init__(self, name):
        self.name = name
        # self.time = datetime.datetime.now().strftime("%H:%M:%S")
        self.status = False

chats = {}

def make_inline_markup(tasks, type):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in range(len(tasks)):
        if not(type == 'done' and tasks[i].status == True):
            item = types.InlineKeyboardButton(f'{i + 1}) {tasks[i].name}', callback_data=f'{type}_{i+1}')
            markup.add(item)
    return markup

def tasks_list(tasks):
    if len(tasks) > 0:
        text = 'Ваши задачи:\n'            
        #  chats[str(call.message.chat.id)] - список
        for i in range(len(tasks)):
            text += f'[{"✅" if tasks[i].status else "❌"}] {i + 1}) {tasks[i].name}\n'
        return text
    else:
        return 'У вас нет задач!'

def add_handler(message):
    task_name = message.text
    if str(message.chat.id) in chats.keys():     
        if task_name in ['📜 Show list', '📌 Add task', '🔨 Done task', '🗑️ Remove task', '🧹 Clear list']:
            bot.reply_to(message, 'Введите корректную задачу!')
            bot.register_next_step_handler(message, add_handler)
            return
        
        chats[str(message.chat.id)].append(Task(task_name))
    else:
        chats[str(message.chat.id)] = [Task(task_name)]
    bot.send_message(message.chat.id, 'Я добавил вашу задачу...')
    

@bot.callback_query_handler(func=lambda call: True)
def callbck_inline(call): # 2
    try:
        if call.message:
            if call.data.split('_')[0] == 'done': #done_1 => ['done', '1']
                task_index = int(call.data.split("_")[1]) - 1
                bot.delete_message(call.message.chat.id, call.message.message_id) # 2
                chats[str(call.message.chat.id)][task_index].status = True
                bot.send_message(call.message.chat.id, f'Вы выполнили задачу №{task_index + 1}')
                
            elif call.data.split('_')[0] == 'remove':
                task_index = int(call.data.split("_")[1]) - 1
                bot.delete_message(call.message.chat.id, call.message.message_id) # 2
                del chats[str(call.message.chat.id)][task_index]
                bot.send_message(call.message.chat.id, f'Вы удалили задачу №{task_index + 1}')
                
    except Exception as e:
        print(e)    

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    elem_1 = types.KeyboardButton('📜 Show list')
    elem_2 = types.KeyboardButton('📌 Add task')
    elem_3 = types.KeyboardButton('🔨 Done task')
    elem_4 = types.KeyboardButton('🗑️ Remove task')
    elem_5 = types.KeyboardButton('🧹 Clear list')
    
    markup.row(elem_1)
    markup.row(elem_2, elem_3)
    markup.row(elem_4, elem_5)
    # print(chats[str(message.chat.id)])
    # print(chats)
    
    bot.send_message(message.chat.id, 'Hello, {0}'. format(message.from_user.first_name), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    id_ch = message.chat.id
    if message.chat.type == 'private':
        if message.text == '🔨 Done task':
            if str(message.chat.id) in chats.keys() and  len([1 for i in chats[str(id_ch)] if i.status == False]) > 0:
                text = tasks_list(chats[str(id_ch)]) + '\n\nКакую задачу вы выполнили?'
                bot.send_message(id_ch, text, reply_markup=make_inline_markup(chats[str(message.chat.id)], 'done')) # 2
            else:
                bot.send_message(id_ch, 'У вас нет задач!')
        elif message.text == '🗑️ Remove task':
            if str(message.chat.id) in chats.keys() and  len(chats[str(id_ch)]) > 0:
                text = tasks_list(chats[str(id_ch)]) + '\n\nКакую задачу удалить?'
                bot.send_message(id_ch, text, reply_markup=make_inline_markup(chats[str(message.chat.id)], 'remove'))
            else:
                bot.send_message(id_ch, 'У вас нет задач!')
            
        elif message.text == '📜 Show list':
            if str(message.chat.id) in chats.keys() and  len(chats[str(id_ch)]) > 0:
                bot.send_message(id_ch, tasks_list(chats[str(id_ch)]))
            else:
                bot.send_message(id_ch, 'У вас нет задач!')
            
        elif message.text == '🧹 Clear list':
            if str(message.chat.id) in chats.keys() and len(chats[str(id_ch)]) > 0:
                chats[str(id_ch)] = []
                bot.send_message(id_ch, 'Я удалил все ваши задачи...')
            else:
                bot.send_message(id_ch, 'У вас нет задач!')
        elif message.text == '📌 Add task':
            bot.send_message(id_ch, 'Введите задачу:')
            bot.register_next_step_handler(message, add_handler)
            

bot.skip_pending=True
bot.polling(none_stop=True)



# 1. Вывод только невыполненных через done
# 1.1 Если все задачи выполнены, то вывести сообщение

# 2. Удаление списка при вызове done, remove
# 2.1 Если все задачи удалены, то вывести сообщение

# 3. Добавить add