# spike-docdb-blowout

An example to compare different document databases.

```
# One-time steps:
mise allow
mise use
poetry install

# In one terminal:
mise run m

# In another terminal:
fastapi dev spike_docdb_blowout
```

## Requirements

We use Mise to manage Python and Poetry, and subsequently Poetry to manage our
Python dependencies.

* [Mise](https://mise.jdx.dev/)
* [Docker](https://www.docker.com/)
