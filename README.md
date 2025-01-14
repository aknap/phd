# Természetesnyelv-feldolgozási modellek társadalomtudományos alkalmazásai és interpretációja
**Doktori értekezéssel kapcsolatos kapcsolatos segédanyagok, kódrészletek, vizualizációk**

Készítette: Knap Árpád Vilmos

Eötvös Loránd Tudományegyetem, Társadalomtudományi Kar, [Szociológia Doktori Iskola](https://tatk.elte.hu/phd), Interdiszciplináris Társadalomkutatások Doktori Program

ELTE Research Center for Computation Social Science ([ELTE RC2S2](https://rc2s2.elte.hu))

Konzulens: Dr. Barna Ildikó (PhD), habilitált egyetemi docens

## A projekt függőségei
Ebben a repozitóriumban található kódok eredetileg Python 3.6-ban kerültek megírásra, azonban Python 3.10 alatt is megfelelően futnak. 

A projekthez szükséges csomagokat a `pip install -r requirements.txt` paranccsal lehet telepíteni. Virtuális környezet használata ajánlott.

Néhány előfeldolgozási feladathoz külső szoftverek szükségesek, amelyeket legegyszerűbben Docker konténerekben lehet telepíteni. Ezek a követelmények kommentekben olvashatók. 

## Ajánlások

### Adatok és fájlformátumok
A repozitóriumban található kódok egy közös input/output formátumot használnak. Ez a formátum egy egyszerű dictionary, ahol a kulcsok a fájlnevek (ezek egyedi azonosítók is egyben), az értékek pedig a szövegek.

Az adatok beolvasásához és elmentéséhez szükséges függvények az `src/common_functions.py` fájlban találhatók. Ezek jelenleg az alábbiak:
- `load_folder_to_dict()`: beolvassa egy txt fájlokat tartalmazó mappa tartalmát egy dictionary-be
- `save_dict_to_txts()`: elmenti egy dictionary tartalmát egy mappába, egyszerű txt fájlokba
- `dump_corpus_to_csv()`: elmenti egy dictionary tartalmát egy CSV fájlba, amely csak a szövegeket tartalmazza (ez például szóbeágyazási modellek inputjaként használható)

Néhány mintakód az adatok beolvasásához, mentéséhez és konvertálásához az `src/files_load_save_example.py` fájlban található.

#### Szövegfáljok (`txt`)
Szövegfájlok használata kisebb méretű korpuszokhoz ajánlott, amelyek maximum néhány ezer darab dokumentumot tartalmaznak. 
Nagyobb korpuszokhoz CSV fájlok vagy SQL adatbázis használata ajánlott, mivel több tíz- vagy százezer darab apró fájl beolvasása időigényes lehet.

A projektben található szövegfájlok esetében a fájlnevek egyben egyedi azonosítók, a fájl tartalma pedig a szöveg. 
A fájlban található szöveg "státuszát" a szülő könyvtár neve határozza meg, például:
- `data/raw/articles`: nyers, feldolgozatlan cikkek szövegét tartalmazza.
- `data/interim/articles_lemmatized`: lemmatizált cikkeket tartalmaz. 
- `data/interim/articles_lemmatized_ner`: lemmatizált cikkeket tartalmaz, amelyekre lefutott a névelemek standardizálását végző kód.
A fent vázolt struktúra segítségével könnyen visszatérhetünk a korpusz valamelyik előző verziójára anélkül, hogy újra kellene futtatni bármelyik korábbi előfeldolgozási lépést.

Az egyszerű txt fájlok beolvasásához és elmentéséhez található függvények az `src/common_functions.py` fájlban találhatók.

#### Táblázatos adatformátumok (`csv`, `tsv`, `xlsx`)
Táblázatos adatformátumok beolvasásához a Pandas csomag ajánlott. Pandas DataFrame-ből egyszerű `id: text` formátumú dictionary készíthető (`df.to_dict(orient = 'index')`), amely használható a repozitóriumban található kódokkal.


## Mappastruktúra
A repozitóriumban található mappastruktúra részben a [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/) ajánlását követi.

- `data/common`: segédfájlok, pl. stopszó listák tárolására
- `data/common/sample_hu_12`: 12 nyers magyar nyelvű újságcikk, a kódok teszteléséhez
- `src/preprocess/hu`: specifikusan magyar nyelvre, előfeldolgozáshoz használható programkódok 
- `src/preprocess`: nem nyelvspecifikus, előfeldolgozáshoz használható programkódok


## Az előfeldolgozás lépései
A következő részben egy általános ajánlás olvasható a különböző előfeldolgozási lépések sorrendjéről.
Az előfeldolgozással kapcsolatban további információk találhatók a disszertáció I.3.3 fejezetében.

Az előfeldolgozási lépések sorrendjét bizonyos projektspecifikus igények bármikor felülírhatják.

1. Az ékezetes karakterek arányának kiszámítása (`detect_accented_chars_ratio.py`). Ez elsősorban rossz helyesírással, ékezetek nélkül írt szövegek (pl. kommentek) kiszűrésére használható.
2. URL-ek, email címek eltávolítása (`urlextract.py`). 
3. Speciális karakterek eltávolítása (lásd a `remove_special()` függvényt a `lemmatize_hunlp.py` fájlban). Ez elsősorban a HuNLP csomaggal történő lemmatizálás esetében releváns, az Emagyar (emtsv) és a HuSpacy esetében nem szükséges.
4. Tokenizálás, lemmatizálás, szófaji szűrések, a szöveg kisbetűsítése, írásjelek eltávolítása (`lemmatize_huspacy.py` vagy `lemmatize_emtsv.py` vagy `lemmatize_hunlp.py`).
5. Névelemfelismerés és standardizálás (`ner.py`).
6. Trigramok összevonása.
7. Bigramok összevonása.
8. A szövegek további standardizálásához manuálisan összeállított listák segítségével bizonyos szavak, kifejezések cseréje.
9. Stopszavak eltávolítása (`stopwords.py`).
10. Gyakoriság szerinti szűrés.

## Modellezéssel kapcsolatos kódok
Az alábbiakban a doktori értekezésben használt modellek egy részének előállításához használt kódok és kódrészletek találhatók.

- `optimal_topic_number.py`: LDA topikmodellek futtatása több topikszámra, koherenciamutatók kiszámítása, PyLDAVis vizualizációk előállítása, dokumentum-topik Excel fájlok mentése, readme fájl mentése. A kód a Gensim LDA Multicore implementációját alkalmazza.
- `glove_phd_stability.R`: GloVe szóbeágyazási modellek előállítása különböző paraméterekkel, a vektorterek stabilitásának vizsgálatához kontextusszavak segítségével.
- `glove_phd_analysis.R`: GloVe szóbeágyazási vektorterekben lévő koszinusztávolságok vizsgálata bizonyos szavak között.

# Hivatkozás és licensz
A repozitóriumban található kódok szabadon felhasználhatók. A kódok alkalmazásának feltétele a kapcsolódó disszertáció hivatkozása:

Knap Árpád (2024). *Természetesnyelv-feldolgozási modellek társadalomtudományos alkalmazásai és interpretációja*. Doktori értekezés, ELTE Szociológia Doktori Iskola.
