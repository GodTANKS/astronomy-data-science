# SGP4 + AI Space Surveillance — Public Beta Launcher

이 디렉터리는 공개 Beta 실행용 런처입니다.

- 실제 Python 소스코드는 GitHub에 평문으로 공개하지 않습니다.
- 공개 저장소에는 암호화된 실행 payload만 보관합니다.
- Streamlit Community Cloud의 `SPACE_BETA_KEY` secret이 있어야 실행됩니다.
- 암호화 payload SHA-256: `54e806a5ccce86375d021fe63837221a6aa28927085470854842b5fb47597e6e`
- 논문 심사 중: 논문 PDF, 활동지 원본, 세부 소스는 비공개입니다.

## Streamlit 배포 설정

- Repository: `GodTANKS/astronomy-data-science`
- Branch: `main`
- Main file path: `apps/space-surveillance/streamlit_app.py`
- Python: 3.12 권장

Secrets:
```toml
SPACE_BETA_KEY = "<private deployment key>"
```