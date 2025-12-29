# RezkaDownloader

### How to use

- download all dependencies:

```python
pip install -r req.txt
```
- check if ffmpeg is installed:
```bash
ffmpeg --version
```
- create `.env` file inside `src/config` folder:
```
KP_KEY: '' # your KinopoiskAPIUnoffical Key
Cookie: '' # gather your cookies from hdrezka
```
- create `manifest.yaml` file with this structure:
``` yaml
  media_type: # 'tv', 'movie'
    - kp_id: int # u can find it on kinopoisk.ru
      hdr_id: int # hdrezka unique identifier (first int in endpoint)
      translator_id: int # identifier of translator (238 for original)
      series: # fill this if media_type is 'tv'
        - season: int # number of season
          episodes: str # use range or list all episodes separated by coma (1-4,5)
      title: str # This would be part of filename
      video_lang: str # (optional) Language of audio in video stream (eng, rus, ..)
      subtitles_lang: str # (optional) Same as video_lang but for subtitles
      video_encoder: str # (optional) Encoder that would be used by ffmpeg, u can find then using `ffmpeg -encoders`
      audio_encoder: str # (optional) same as previous one
      format: str # (optional) format of output file for ffmpeg
```
- run start.py file
- find all your downloadings in `src/downloads` folder

- in case of errors consult log file `all.log` in `src/logs/` folder


copyright @ [av3r6un](https://github.com/av3r6un)

Feel free to support me. [Boosty](https://boosty.to/av3rgun)
