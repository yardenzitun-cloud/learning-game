# Learning Adventure (הרפתקת הלמידה)

A tablet learning game for kids, in Hebrew (plus an English track for grade 5). Kids get a profile, play short stages of questions, earn coins, and spend them in a shop to decorate their own room. Progress can sync between devices with a family code.

Live version: https://yardenzitun-cloud.github.io/learning-game/

## What's in the repo

| File | What it is |
|---|---|
| `index.html` | The whole app: HTML, CSS and JavaScript in one file. No build step, no framework. |
| `voice_<track>_<n>.js`, `voice_extra.js` | Recorded voice clips (mp3, base64) bundled per track. Loaded on demand. |
| `sw.js` | Service worker. Caches the app so it works offline. |
| `manifest.json`, `icon-*.png` | Lets the app be added to the tablet home screen. |
| `tools/` | Python scripts for recording new voice clips. Not used by the app at runtime. |

## Getting your own copy running

1. Create a GitHub account and fork this repo.
2. In your fork: Settings → Pages → Source: Deploy from a branch → Branch: `main`, folder `/ (root)` → Save.
3. After a minute or two the app is live at `https://<your-user>.github.io/learning-game/`.
4. Set up your own Firebase project (next section) before your kids start using it.

To work on it locally, open `index.html` from any static web server (for example `python3 -m http.server` in the repo folder, then go to http://localhost:8000). Opening the file directly also works for most things.

## Firebase (device sync) – replace with your own

Sync uses Firebase Anonymous Auth and Firestore over plain REST calls (no Firebase SDK). The project details are hard-coded in `index.html`:

```js
const FB={key:'AIzaSy...',proj:'learning-game-7c676'};
```

That is the original author's project. If you leave it, your family's data is stored there. To use your own:

1. Go to https://console.firebase.google.com and create a project (the free Spark plan is enough).
2. Build → Authentication → Get started → Sign-in method → enable **Anonymous**.
3. Build → Firestore Database → Create database (production mode, any region).
4. Firestore → Rules, paste this and publish:

   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{db}/documents {
       match /families/{code} {
         allow get, create, update: if request.auth != null;
       }
     }
   }
   ```

5. Project settings → General → Your apps → add a Web app. Copy `apiKey` and `projectId`.
6. In `index.html` replace the `FB` line with your values: `key` = apiKey, `proj` = projectId.

`get` (not `read`) matters: `read` would also allow listing the whole collection, which would let anyone with the API key see every family's code and data. With `get` you can only open a document whose code you already know. The family code is the only thing that separates one family's data from another's, so treat it like a password. Each family is one Firestore document at `families/<code>`, holding the whole app state as a JSON string.

Sync is optional. Without a family code the app works fully and keeps everything in the browser's `localStorage` (key `kidsLearnApp.v3`).

## How the code is organized (index.html)

Everything is in one `<script>` block. In rough order from top to bottom:

- **Helpers**: random numbers, shuffle, small HTML builders (`R`, `pick`, `shuffle`, `objs`, `eq` and so on).
- **Voice**: `speak()` plays a recorded clip if one exists for the exact text (`CLIPS` map → `voice_*.js` bundles), and falls back to the browser's speech synthesis if not. `gx()` adjusts boy/girl wording.
- **Question generators**: one function per question type. Each returns a question object (prompt, visual, options, correct answer). Naming:
  - `g*` – grade 1 and grade 5 math (`gCount`, `gAdd`, `gFracPart`, `gWord2`...)
  - `heb*`, `q*` – grade 1 Hebrew reading (letters, syllables, words, by `HEB_STAGES`)
  - `e*` – grade 5 English (`eLetterR`, `eList`, `eMagic`...), word lists in `EW`
  - `t*` – kindergarten (colors, shapes, numbers, animals)
  - `m*` – multiplication table track
  - grade 8 English (`g8` track): word lists in `V8` and `R8`, grammar items in `GR8`, lessons in `L8`, generators `gGap`, `gOpp`, `gComp`, `gSilent`, `gSoftHard`, `gPastForm`, `gIng`
  - English distractors are built by `lookAlike()` / `nearest()`: options that differ by a letter or vowel, so the word has to be read
- **Lessons**: short explanations shown before a new topic. `LESSON` (grade 1 math), `TLES` (kindergarten), `ML` (multiplication) and the Hebrew lesson builders. `LMAP` connects a stage title to its lesson.
- **`SUBJECTS`**: the curriculum. Each subject is a list of stages built with `st(title, generator, chapterTitle?)`. The order of the list is the order on the kid's map.
- **`TRACKS`**: which subjects each track gets, plus theme text. Current tracks: `tohar` (kindergarten), `yonatan` (grade 1), `tamar` (grade 5), `g8` (grade 8 English, Ready To Go!). The track names are just internal ids; parents create profiles with any name and pick a track.
- **`SHOP`, `ART`, `FURN`**: shop items per track. Furniture is drawn as inline SVG (`ART`) and can be dragged around the room.
- **State and sync**: `defKid`, `load`, `save`, then the Firebase functions (`fbToken`, `fbGet`, `mergeState`, `syncNow`).
- **Screens**: `home`, `kidHome`, `map`, `runStage`/`showQ`/`answer`, `shop`, `room`, `parent` (parent area, protected by a PIN, default `1234`).

## Adding content

**A new stage in an existing subject.** Find the subject in `SUBJECTS` and add a line:

```js
st('חיבור עד 20', ()=>gAddPlain(20)),
```

The third argument starts a new chapter heading on the map. `mix(genA, genB, ...)` makes a stage that mixes question types.

**A new question type.** Write a generator next to the similar ones. Copy an existing generator and change it; the cleanest small examples are `gAddPlain` and `gCompare`. Keep the same return shape as the function you copied.

**A new subject.** Add an entry to `SUBJECTS` (`title`, `book`, `ic` icon, `qn` questions per stage, `stages`) and add its key to the `subjects` list of the right track in `TRACKS`.

**A new track (another grade).** Add an entry to `TRACKS` and `TRACK_LABEL`, and give it a shop list in `SHOP` (and `FURN` if you want furniture). It will then show up when a parent creates a profile.

Stage progress is stored by subject key and stage index, so add new stages at the end of a subject if kids already have progress in it. Inserting in the middle shifts what counts as "done".

After changing files that the service worker caches, bump the cache name in `sw.js` (`const C='lg-v7'` → `'lg-v8'`) so tablets pick up the new version. Kids may need to close and reopen the app once.

## Voice recordings

The app speaks every instruction and question. A recorded clip is used when one exists for the exact sentence; anything new falls back to the tablet's built-in Hebrew voice. So new content works right away, it just sounds different until it's recorded.

The original recordings were made with Google Gemini TTS (voice "Leda") using the scripts in `tools/`. See `tools/README.md`. In short:

1. `collect4.py` opens the app in headless Chrome and lists every sentence the app can say.
2. Compare that list with `tools/rec_leda_all.json` to find the new sentences.
3. `batchall.py` records them with the Gemini batch API.
4. `build6.py` rebuilds the `voice_*.js` bundles and the `CLIPS` map in `index.html`.

You need your own Gemini API key. Keep it in a local file (the scripts read `/home/claude/tts/.key`) and never commit it. The scripts were written for one specific environment, so the paths at the top of each script will need adjusting on your machine. They need Python 3, `ffmpeg`, and Playwright with Chrome.

## Things to know

- The app is right-to-left Hebrew. Boy/girl wording is chosen from the profile's gender; texts for younger kids are written with niqqud.
- All images are emoji or inline SVG drawn in code. There are no image files apart from the app icons.
- The parent PIN only keeps kids out of the settings. It is not real security.
