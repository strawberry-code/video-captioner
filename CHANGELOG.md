# Changelog

## [1.1.0] - 2026-02-02

### Added
- Supporto per file audio come input (mp3, wav, flac, aac, ogg, m4a, wma, opus)
- Rilevamento automatico del tipo di media (video/audio)
- Funzione `convert_audio()` per convertire file audio nel formato richiesto da Whisper
- Validazione dei formati supportati con messaggi di errore chiari

### Changed
- Rinominato il progetto da "Video Captioner" a "Media Captioner"
- L'argomento CLI ora accetta qualsiasi file media supportato
- Output adattato in base al tipo di input (video genera anche il file con sottotitoli, audio genera solo SRT e transcript)

## [1.0.0] - 2026-02-02

### Added
- Trascrizione automatica con OpenAI Whisper
- Correzione grammaticale con LanguageTool
- Generazione sottotitoli burned-in e soft
- Output: video con sottotitoli, file SRT, transcript testuale
