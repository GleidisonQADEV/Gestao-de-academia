Você é um agente de release do projeto LegacyBJJ. Execute os passos abaixo em ordem, sem pular nenhum.

## 1. Verificar estado do repositório

- Rode `git status` para garantir que não há mudanças não commitadas. Se houver, avise o usuário e **pare**.
- Rode `git log --oneline -5` para mostrar os últimos commits.

## 2. Ler a versão atual

- Leia `src/version.py` e extraia o valor de `APP_VERSION`.
- Leia `LegacyBJJ.spec` e confirme as versões em `CFBundleShortVersionString` e `CFBundleVersion`.
- Exiba a versão atual para o usuário.

## 3. Determinar a nova versão

Pergunte ao usuário qual tipo de release deseja:
- **patch** — correção de bug (ex: 1.0.0 → 1.0.1)
- **minor** — nova funcionalidade (ex: 1.0.0 → 1.1.0)
- **major** — mudança grande (ex: 1.0.0 → 2.0.0)

Ou o usuário pode informar diretamente o número (ex: `1.2.0`).

Calcule e confirme a nova versão com o usuário antes de continuar.

## 4. Atualizar os arquivos de versão

Atualize a versão nos seguintes arquivos:

**`src/version.py`** — altere o valor de `APP_VERSION`:
```python
APP_VERSION = "NOVA_VERSAO"
```

**`LegacyBJJ.spec`** — altere as duas ocorrências dentro do `info_plist`:
```python
'CFBundleShortVersionString': 'NOVA_VERSAO',
'CFBundleVersion':            'NOVA_VERSAO',
```

## 5. Commit do bump de versão

```bash
git add src/version.py LegacyBJJ.spec
git commit -m "chore: bump version to vNOVA_VERSAO"
git push origin main
```

## 6. Criar e publicar a tag

```bash
git tag vNOVA_VERSAO
git push origin vNOVA_VERSAO
```

## 7. Confirmar

- Exiba a URL da release no GitHub: `https://github.com/GleidisonQADEV/Gestao-de-academia/actions`
- Informe que o GitHub Actions está compilando o `.dmg` e o `.exe` e que a release estará disponível em ~10 minutos em: `https://github.com/GleidisonQADEV/Gestao-de-academia/releases`
