# razbor-failov

Переносимый Codex skill для разбора папок с юридическими и административными документами: содержательное переименование файлов, сборка изображений в упорядоченный PDF и обязательный финальный аудит.

Skill обобщает проверенный рабочий процесс, но не содержит документов, персональных данных или иных материалов исходного дела.

## Что входит

- `SKILL.md` — основной рабочий процесс и правила безопасности;
- `references/` — правила наименования и чек-лист финального аудита;
- `scripts/scan_inventory.py` — инвентаризация папки;
- `scripts/build_image_pdf.py` — PDF «одно изображение — одна страница» с прямым или обратным порядком и манифестом SHA-256;
- `scripts/apply_rename_plan.py` — проверка и безопасное двухэтапное переименование;
- `scripts/verify_filing_names.py` — сверка формата имен и заявленного числа листов;
- `scripts/self_test.py` — автономная проверка переносимости.

## Установка из приватного GitHub-репозитория

Сначала настройте доступ к приватному репозиторию через GitHub CLI (`gh auth login`) или SSH-ключ. Не вставляйте персональный токен в адрес репозитория, команды или файлы skill.

### Windows PowerShell

```powershell
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex' }
$skillsRoot = Join-Path $codexRoot 'skills'
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
git clone https://github.com/aleksskott2000-cyber/razbor-failov-skill.git (Join-Path $skillsRoot 'razbor-failov')
python -m pip install pypdf Pillow reportlab python-docx
python (Join-Path $skillsRoot 'razbor-failov\scripts\self_test.py')
```

### macOS или Linux

```bash
CODEX_ROOT="${CODEX_HOME:-$HOME/.codex}"
mkdir -p "$CODEX_ROOT/skills"
git clone git@github.com:aleksskott2000-cyber/razbor-failov-skill.git "$CODEX_ROOT/skills/razbor-failov"
python3 -m pip install pypdf Pillow reportlab python-docx
python3 "$CODEX_ROOT/skills/razbor-failov/scripts/self_test.py"
```

Для визуальной проверки PDF также нужен Poppler (`pdftoppm`/`pdftotext`). После установки перезапустите Codex или откройте новую задачу.

## Использование

Пример запроса:

```text
Используй $razbor-failov. Сначала прочитай инструкции в TXT-файлах, затем переименуй документы по содержанию и собери фотографии в PDF в обратном порядке.
```

Каноническое имя skill — `$razbor-failov`: формат Codex допускает в имени строчные латинские буквы, цифры и дефисы.

## Обновление

```powershell
git -C (Join-Path $skillsRoot 'razbor-failov') pull --ff-only
```

## Важные ограничения

- Сначала полностью читаются локальные инструкции, затем изменяются файлы.
- Старое имя используется только как подсказка; реквизиты берутся из содержания.
- Неясные даты и номера не придумываются.
- Исходные изображения не удаляются.
- Перед реальным переименованием обязателен dry-run, после него — содержательный и визуальный аудит.
