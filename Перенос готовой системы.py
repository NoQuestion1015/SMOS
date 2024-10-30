import os
import shutil
import customtkinter as ctk

# Путь к файлу version.txt и changelog.txt
version_file_path = '/home/noquestion/Рабочий стол/SMOS/version.txt'
changelog_file_path = '/home/noquestion/Рабочий стол/SMOS/changelog.txt'

# Предустановленные фразы для обновления
update_phrases = [
    "Исправление ошибок",
    "Улучшение функций",
    "Оптимизация производительности",
    "Добавление новых возможностей",
    "Улучшение интерфейса",
]

def get_current_version():
    if os.path.exists(version_file_path):
        with open(version_file_path, 'r') as file:
            return file.read().strip()
    return None

def update_version(is_update, is_patch=False):
    current_version = get_current_version()
    if current_version:
        major, minor, *patch = map(int, current_version.split('.'))
        patch = patch[0] if patch else 0  # Если патч отсутствует, ставим значение по умолчанию

        if is_patch:
            new_version = f"{major}.{minor}.{patch + 1}"  # Увеличиваем патч-версию
        elif is_update:
            new_version = f"{major}.{minor + 1}.0"  # Увеличиваем минорную версию, сбрасываем патч
        else:
            new_version = f"{major + 1}.0.0"  # Переход к следующей основной версии, сбрасываем минорную и патч

        # Обновляем файл version.txt
        with open(version_file_path, 'w') as file:
            file.write(new_version)
        
        return new_version
    return None

def create_new_folder_and_copy_files(new_version):
    new_folder_path = f"/home/noquestion/Рабочий стол/SMOS/SMOS {new_version}"
    os.makedirs(new_folder_path, exist_ok=True)

    # Копируем все файлы из текущей папки скрипта
    current_directory = os.path.dirname(os.path.abspath(__file__))
    for item in os.listdir(current_directory):
        source_path = os.path.join(current_directory, item)
        destination_path = os.path.join(new_folder_path, item)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            shutil.copy2(source_path, destination_path)

def log_changes(new_version, change_description):
    with open(changelog_file_path, 'a') as file:
        file.write(f"{new_version} - {change_description}\n")

def show_version_dialog():
    current_version = get_current_version()
    if not current_version:
        print("Файл с версией не найден.")
        return

    # Создаем окно с выбором
    ctk.set_appearance_mode("dark")
    app = ctk.CTk()
    app.geometry("400x400")
    app.title("Обновление версии")

    label = ctk.CTkLabel(app, text=f"Текущая версия: {current_version}")
    label.pack(pady=10)

    change_type = None
    new_version = None

    def on_update_click():
        nonlocal change_type, new_version
        change_type = "update"
        new_version = update_version(is_update=True)
        show_change_input()

    def on_new_version_click():
        nonlocal change_type, new_version
        change_type = "new"
        new_version = update_version(is_update=False)
        show_change_input()

    def on_patch_update_click():
        nonlocal change_type, new_version
        change_type = "patch"
        new_version = update_version(is_update=True, is_patch=True)
        show_change_input()

    update_button = ctk.CTkButton(app, text="Обновление текущей версии", command=on_update_click)
    update_button.pack(pady=5)

    new_version_button = ctk.CTkButton(app, text="Новая версия", command=on_new_version_click)
    new_version_button.pack(pady=5)

    patch_update_button = ctk.CTkButton(app, text="Патч-обновление", command=on_patch_update_click)
    patch_update_button.pack(pady=5)

    def show_change_input():
        # Удаляем кнопки выбора
        update_button.pack_forget()
        new_version_button.pack_forget()
        patch_update_button.pack_forget()

        # Отображаем текущую и новую версии
        version_label = ctk.CTkLabel(app, text=f"Текущая версия: {current_version} → {new_version}")
        version_label.pack(pady=10)

        if change_type in ["update", "patch"]:
            ctk.CTkLabel(app, text="Выберите заготовленное изменение:").pack(pady=10)
            selected_phrase = ctk.StringVar(value=update_phrases[0])

            for phrase in update_phrases:
                ctk.CTkRadioButton(app, text=phrase, variable=selected_phrase, value=phrase).pack(anchor='w')

            custom_change_text = ctk.CTkTextbox(app, height=5)
            custom_change_text.pack(pady=10)

            def confirm_update():
                description = selected_phrase.get() if selected_phrase.get() else custom_change_text.get("1.0", "end").strip()
                log_changes(new_version, description)
                create_new_folder_and_copy_files(new_version)
                app.destroy()

            confirm_button = ctk.CTkButton(app, text="Подтвердить обновление", command=confirm_update)
            confirm_button.pack(pady=5)

        elif change_type == "new":
            ctk.CTkLabel(app, text="Введите описание изменений для новой версии:").pack(pady=10)
            new_change_text = ctk.CTkTextbox(app, height=5)
            new_change_text.pack(pady=10)

            def confirm_new_version():
                description = new_change_text.get("1.0", "end").strip()
                log_changes(new_version, description)
                create_new_folder_and_copy_files(new_version)
                app.destroy()

            confirm_button = ctk.CTkButton(app, text="Подтвердить новую версию", command=confirm_new_version)
            confirm_button.pack(pady=5)

    app.mainloop()

if __name__ == "__main__":
    show_version_dialog()
