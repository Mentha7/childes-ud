# chatconllu
  Conversion scripts between CHILDES CHAT format and UD CoNLL-U format.

## Installation
----
#### Prerequisites

Python Version >= 3.6

I'm using [poetry](https://python-poetry.org/) for dependency management. Follow these [instructions](https://python-poetry.org/docs/#installation) to install poetry.
After cloning this repo, change directory to the `chatconllu` folder with `Makefile`:

```shell
cd chatconllu
make install
```

#### Install chatconllu

```
make installchatconllu
```

## Example Usage
----
### From .cha files to .conllu files

```
chatconllu <CHILDES databases dir> <database name(s)>
```

**Example**

If your Brown Corpus is stored in `./tests/eng/Brown` and you wish to convert only the .cha files in `Adam` and `Eve` but not `Sarah`, you should use the following command:

```
chatconllu ./tests/eng/Brown Adam Eve
```
The output .conllu files will be in the same folder.

----

### From .conllu files to .cha files

Use `-f` or `--format` to specify the input format, defualts to `cha`, accepts `cha` and `conllu`.

```
chatconllu <CHILDES databases dir> -f conllu <database name(s)>
```

**Example**

If you wish to convert only the .conllu files back, use:

```
chatconllu ./tests/eng/Brown -f conllu Adam Eve
```
The output .cha files will  *NOT*  be in the same folder, they will appear in `out/`

----

### Suppress existing dependent tiers

If you'd like to disregard the `%mor` (`--no-mor`) or `%gra` (`--no-gra`) tiers (or both) and mute the `MISC` field (`--no-misc`), try:

```
chatconllu <CHILDES databases dir> <database name(s)> --no-mor --no-gra --no-misc
```

----

### Generating new dependent tiers


If you, for some reason, would like to generate a new (and empty) `%mor` (`--new-mor`) or `%gra` (`--new-gra`) tiers (or both), try:

```
chatconllu <CHILDES databases dir> <database name(s)> --new-mor --new-gra
```

Empty values are represented by `_`.

However, if you pass .conllu files through [UDPipe](https://ufal.mff.cuni.cz/udpipe) and want to generate dependent tiers based on the augmented information, you could use:

```
chatconllu <CHILDES databases dir> <database name> -f conllu -fn <processed conllu file> --cnl --pos
```
`-fn`: specifies a filename (without extension)
`--cnl`: generates a `%cnl` tier, handles syntax (dependency relations), it's similar to `%gra` 
`--pos`: generates a `%pos` tier, handles morphology (without features), it's similar to `%mor` 

----

### Validating .cha files

#### Using CLAN CHECK Program
- install CLAN
- open .cha file with CLAN
- run CHECK

#### Using Chatter.jar
**Prerequisites**
- at least Java 8
- download `chatter.jar` and follow the instructions [here](https://www.talkbank.org/software/chatter.html).
- commandline:
```
java -cp <path to chatter.jar> org.talkbank.chatter.App -inputFormat cha -outputFormat xml -tree <cha files dir> -outputDir <output dir>
```

----

### Validating .conllu files

**Prerequisites**
- clone [UniversalDependencies/tools/](https://github.com/UniversalDependencies/tools) or download [UniversalDependencies/tools/data/](https://github.com/UniversalDependencies/tools/tree/master/data).
- use `validate.py` from [UniversalDependencies/tools/validate.py](https://github.com/UniversalDependencies/tools/blob/master/validate.py).

```
python <path to validate.py> --lang <2-letter language code> --level <level from 1 to 5> <path to conllu file>
```

Current state of chatconllu supports **max level-2** tests (tested on English with Brown Corpus).

<!-- ## Project Structure
----

```

``` -->
