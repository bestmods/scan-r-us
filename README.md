This was a pretty neat web scraper I made for [Best Mods](https://bestmods.io) in early-mid 2024. It was private until now.

This web scraper extracted data from game mods from a few public modding websites and would send API requests to Best Mods' REST API that then added the mod to the website that linked back to the original source. This resulted in over 100,000 mods being added to the Best Mods website that served as an index for game mods.

This project does not contain any private web scraper classes created to extract data from popular modding websites for obvious reasons.

While the Best Mods website is still online, it is no longer maintained which is why I'm releasing the source code of this once private web scraper. There may be a chance I work on Best Mods again in the future, but I'd really want to overhaul the front-end design entirely.

## Running
You can run this project by using `python3` like below.

```bash
python3 src/main.py
```

## CLI Usage
The following command line arguments are supported.


| Name | Default | Description |
| ---- | ------- | ----------- |
| `-c --cfg` | `./settings.json` | The path to the config file. |
| `-l --list` | - | Prints the contents of the config and exits. |

## Configuration
Configuration is read from a file on disk and parsed using JSON. By default, the `./settings.json` file is loaded, but you may change this using the CLI argument above.

I'd recommend copying the [`./settings.example.json`](./settings.example.json) to `./settings.json`.

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `debug` | int | `1` | The debug level.
| `logFile` | string | `NULL` | The log file to write debug messages to. |
| `binaryPath` | string | `/usr/bin/geckodriver` | The path to the Geckodriver. |
| `database` | Database Object | `{}` | The database object that contains details on the Scan R Us database. |
| `userAgents` | string array | `["Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"]` | A list of user agents to use with the web scraper. |
| `parsers` | Parser Array | `[]` | A list of parsers. |
| `api` | API Object | `{}` | The REST API object. |

### Database Object
The database object contains details on the database.

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `host` | string | `localhost` | The database host. |
| `name` | string | `scanrus` | The database name. |
| `user` | string | `root` | The database user. |
| `pass` | string | `""` | The database password. |
| `port` | int | `5432` | The database port. |
| `sizeLimit` | int | `25000` | The max size of the database. |

### Parser Object
The parser object is used to initialize a specific web scraper.

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `disabled` | bool | `false` | Whether to disable this scraper. |
| `url` | string | `NULL` | The URL of the website to scrape from (just the domain name). |
| `protocol` | string | `https` | The website's web protocol (typically `http` or `https`). |
| `categories` | String => Int Mapping | `{}` | Maps the URL category names to the IDs on Best Mods. |
| `catsChildren` | String => Int Mapping | `{}` | Maps the URL category child names to the IDs on Best Mods. |
| `findEnabled` | bool | `true` | If enabled, this parser finds new mods to add for parsing. |
| `findIntervalMin` | int | `300` | The minimum amount of time between cycles to find mods. |
| `findIntervalMax` | int | `600` | The maximum amount of time between cycles to find mods. |
| `parseEnabled` | int | `true` | If enabled, this parser parses and extracts data from mods. |
| `parseIntervalMin` | int | `150` | The minimum amount of time between cycles to parse mods. |
| `parseIntervalMax` | int | `300` | The maximum amount of time between cycles to parse mods. |
| `parseExisting` | bool | `false` | Whether to parse mods that already existed in the database. |
| `parseNew` | bool | `true` | Whether to parse mods that aren't already stored in the database. |
| `addEnabled` | bool | `true` | Whether to add or update mods via API request to the Best Mods's API. |
| `addIntervalMin` | int | `30` | The minimum amount of time between cycles to add mods. |
| `addIntervalMax` | int | `60` | The maximum amount of time between cycles to add mods. |
| `addExisting` | bool | `false` | Whether to add or update existing mods. |
| `addNew` | bool | `true` | Whether to add or update new mods. |
| `testMode` | bool | `false` | If enabled, doesn't update the Best Mods's API. |
| `skipNullCategory` | bool | `true` | Whether to skip null categories. |
| `logPagFailOutput` | bool | `true` | If true, logs the output of the webpage if it fails. Useful for debugging. |
| `cleanupBanners` | bool | `true` | Removes mod image banners locally to save space. |
| `avoidIds` | string array | `[]` | A list of IDs to not add or update. |

### REST API Object
The REST API object contains details on the Best Mods API.

| Name | Type | Default | Description |
| ---- | ---- | ------- | ----------- |
| `host` | string | `localhost` | The API host. |
| `token` | string | `NULL` | The token to set through the request headers. |
| `limit` | int | `5` | The maximum amount of mods to update at a time. |
| `preTime` | int | `5` | Only set mods to update that are last updated before *x* seconds ago (where *x* is `preTime`). |
| `intervalMin` | int | `30` | The minimum amount of time in seconds to run an update cycle. |
| `intervalMax` | int | `60` | The maximum amount of time in seconds to run an update cycle. |

## Credits
* [Christian Deacon](https://github.com/gamemann)