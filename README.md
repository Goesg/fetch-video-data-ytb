# fetch-video-data-ytb

Extrai metadados de playlists do YouTube e persiste localmente em JSON.

---

## Abordagem técnica

O projeto usa **yt-dlp** com `extract_flat=True` — sem download de vídeo, apenas metadados. Essa abordagem foi escolhida em relação à YouTube Data API oficial pelos seguintes motivos:

- Zero configuração de credenciais: roda imediatamente em qualquer máquina
- Trata nativamente vídeos privados, removidos e indisponíveis
- Nenhum limite de quota por dia
- Única dependência de runtime
- Comunidade ativa que mantém compatibilidade com mudanças do YouTube

---

## Requisitos

- Python 3.10 ou superior
- pip

---

## Instalação

```bash
# Clone o repositório
git clone <url-do-repo>
cd fetch-video-data-ytb

# Crie e ative um ambiente virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate

# Instale o projeto e suas dependências
pip install -e .
```

Para instalar também as dependências de desenvolvimento (testes):

```bash
pip install -e ".[dev]"
```

---

## Execução

### Forma básica

```bash
python -m app.main "https://www.youtube.com/playlist?list=PLxxxxxxx"
```

### Com flag explícita

```bash
python -m app.main --url "https://www.youtube.com/playlist?list=PLxxxxxxx"
```

### Especificando o arquivo de saída

```bash
python -m app.main "URL" --output outputs/minha_playlist.json
```

### Especificando apenas o diretório de saída

```bash
python -m app.main "URL" --output-dir /tmp/playlists
```

### Com logs verbose

```bash
python -m app.main "URL" --verbose
```

---

## Saída

Os arquivos JSON são gravados em `outputs/` com o nome derivado do título da playlist:

```
outputs/My_Playlist_Title__PLxxxxxxx.json
```

### Estrutura do JSON

```json
{
  "playlist": {
    "source_url": "https://www.youtube.com/playlist?list=PLxxxxxxx",
    "playlist_id": "PLxxxxxxx",
    "title": "Nome da Playlist",
    "total_items": 42,
    "extracted_at": "2026-01-01T12:00:00Z"
  },
  "items": [
    {
      "video_id": "abc123",
      "playlist_id": "PLxxxxxxx",
      "playlist_title": "Nome da Playlist",
      "original_title": "Pink Floyd - Comfortably Numb (Remastered 2011)",
      "normalized_title": "pink floyd - comfortably numb",
      "artist": "Pink Floyd",
      "track": "Comfortably Numb",
      "year": 2011,
      "uploader": "Pink Floyd",
      "channel": "Pink Floyd",
      "duration_seconds": 382,
      "url": "https://www.youtube.com/watch?v=abc123",
      "position": 1,
      "availability_status": "available",
      "extraction_confidence": "high",
      "extraction_notes": []
    }
  ]
}
```

### Campos de controle de qualidade

| Campo | Valores possíveis | Significado |
|---|---|---|
| `availability_status` | `available`, `private`, `removed`, `unavailable`, `unknown` | Estado do vídeo na plataforma |
| `extraction_confidence` | `high`, `medium`, `low` | Confiança no parsing artista/faixa |
| `extraction_notes` | lista de strings | Observações do processo de extração |

---

## Parser de títulos

O parser tenta separar artista e faixa a partir de padrões comuns:

| Padrão | Resultado |
|---|---|
| `Artist - Track` | artist=Artist, track=Track, confidence=high |
| `Artist - Track` (em-dash) | idem |
| `Artist \| Track` | idem (pipe) |
| `Artist feat. X - Track` | artist=Artist feat. X, confidence=medium |
| `Artist ft. X - Track` | idem |
| `Artist x Other - Track` | idem |
| Sem separador claro | artist=null, track=null, confidence=low |

Tags removidas automaticamente do título normalizado: `(Official Video)`, `(Official Audio)`, `[Lyrics]`, `[HD]`, `(Remastered)`, `(Visualizer)`, `(Audio)`, `(Explicit)`, `(Extended)`, etc.

O parser é **heurístico**: quando a separação for ambígua, ele não força uma interpretação — mantém `null` e registra a incerteza em `extraction_notes`.

---

## Testes

```bash
python -m pytest tests/ -v
```

Cobertura dos testes:
- Validação de URLs de playlist
- Extração de playlist ID
- Parser de títulos (separadores, feat, collab, remoção de tags, extração de ano)
- Exportação para JSON (estrutura, campos, encoding, ordenação, diretório)

---

## Estrutura do projeto

```
fetch-video-data-ytb/
  README.md
  pyproject.toml
  .gitignore
  app/
    __init__.py
    cli.py                  # Parsing de argumentos CLI
    main.py                 # Orquestrador principal
    models/
      playlist.py           # PlaylistMetadata dataclass
      track_item.py         # TrackItem dataclass
    services/
      metadata_parser.py    # Heurísticas de parsing de título
      playlist_extractor.py # Integração com yt-dlp
      export_service.py     # Serialização e escrita do JSON
    utils/
      validators.py         # Validação de URLs
      text_normalizer.py    # Limpeza e normalização de títulos
      logging_utils.py      # Configuração de logging
  outputs/                  # Arquivos JSON gerados (gitignore)
  tests/
    test_validators.py
    test_metadata_parser.py
    test_export_service.py
```

---

## Limitações conhecidas (MVP)

1. **Parser de títulos é heurístico**: funciona bem para o padrão `Artista - Faixa`, mas falha em títulos não convencionais (podcasts, vídeos institucionais, títulos sem separador).

2. **`extract_flat=True` limita metadados por item**: duração e uploader podem ser `null` dependendo do tipo de entrada da playlist. Uma segunda passagem com extração completa por item traria mais dados, mas aumentaria o tempo de execução.

3. **Sem cache**: cada execução re-extrai tudo do zero. Playlists grandes são lentas.

4. **Sem retry automático**: se yt-dlp falhar por rate limiting ou erro de rede, a execução para.

5. **yt-dlp pode quebrar**: quando o YouTube muda sua interface interna, yt-dlp pode parar de funcionar temporariamente. Solução: manter yt-dlp atualizado (`pip install --upgrade yt-dlp`).

6. **Sem detecção de duplicatas**: a mesma playlist pode ser extraída múltiplas vezes gerando arquivos distintos.

---

## Próximos passos sugeridos

1. **Cache local por playlist_id**: evitar re-extração desnecessária, comparar com extração anterior e indicar o delta.

2. **Modo incremental**: detectar itens novos vs. já extraídos, útil para playlists que crescem ao longo do tempo.

3. **Parser melhorado**: usar lista de artistas conhecidos ou `rapidfuzz` para melhorar confiança na separação artista/faixa.

4. **Extração completa por item**: modo opcional (`--full`) para buscar mais metadados por vídeo (tags, descrição, etc.).

5. **Migração para SQLite**: os JSONs gerados são naturalmente importáveis com `json_each()`.

6. **Validação de schema com Pydantic**: garantir integridade da saída com versionamento do schema.
