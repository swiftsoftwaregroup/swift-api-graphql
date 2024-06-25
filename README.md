# swift-api-graphql

This project illustrates how one would go about implementing a GraphQL Web API in Python using FastAPI and Strawberry. 

This project was created by copying the [swift-api-rest](https://github.com/vkantchev/swift-api-rest) project and refactoring from REST to GraphQL. 

Currently for simplicity the database is just one table. However in a real world application there should probably be a separate table for Author and a BookAuthor table that links Books and Authors. See [Additional Considerations](https://github.com/vkantchev/swift-api-rest?tab=readme-ov-file#additional-considerations) in `swift-api-rest` for details.

## Setup

* [Setup for macOS](./docs/setup-macos.md)
* [Setup for Ubuntu Linux](./docs/setup-linux.md)

## Run

```bash
source configure.sh

./watch.sh
```

Open the Graph<i>i</i>QL Explorer UI:

```bash
open http://127.0.0.1:8001/graphql
```

![graphiql-ui](./docs/graphiql-ui.png)

### Add a book

Paste this GraphQL code and click the `play` button:

```graphql
mutation {
    createBook(book: {
        title: "Test Book",
        author: "Test Author",
        datePublished: "2023-01-01",
        coverImage: "http://example.com/cover.jpg"
    }) {
        id
        title
        author
        datePublished
        coverImage
    }
}
```

### Query All Books

Paste this GraphQL code and click the `play` button:

```graphql
query {
    books {
        id
        title
        author
        datePublished
        coverImage
    }
}
```

## Updating the code

```bash
source configure.sh
```

Open the project directory in Visual Studio Code:

```bash
code .
```

## Development

Format it with the [black](https://black.readthedocs.io/en/stable/) formatter:

```sh
black .
```

Correct the import order with [isort](https://pycqa.github.io/isort/):

```sh
isort .
```

Verify the typing:

```sh
mypy src/
```

Run the tests (from the command line):

```sh
pytest
```

Generate test coverage report:

```bash
coverage run -m pytest && coverage combine && coverage report
```

Run tests in multiple python environments (will run for 3.12, 3.11, 3.10):

```sh
hatch run test
```

## Deploy to AWS

### AWS Amplify CLI

Follow [Set up Amplify CLI](https://docs.amplify.aws/gen1/javascript/tools/cli/start/set-up-cli) to install the AWS Amplify CLI.

### Deploy

Initialize the Amplify project:

```bash
amplify init
```

Enable container-based deployments (advanced option):

```bash
amplify configure project
```

Add API backend:

```bash
amplify add api
```

Copy app code (replace `swiftapigraphql` with the resource name that Amplify generates for you):

```bash
amplify_dir=./amplify/backend/api/swiftapigraphql/src

# App 
cp -pr src $amplify_dir/
cp -p requirements.txt $amplify_dir/

# Docker
cp -p docker/Dockerfile $amplify_dir/
cp -p docker/docker-compose.yml $amplify_dir/
```

Deploy service:

```bash
amplify push
```

NOTE:

* `amplify push`  will build all your local backend resources and provision it in the cloud.

* `amplify publish` will build all your local backend and frontend resources (if you have hosting category added) and provision it in the cloud.

## Run in Podman / Docker 

> In order to do this you will need Podman. See [Setup Podman on macOS](./docs/setup-podman-macos.md) for details.

Rebuild container image and start container:

```bash
inv podman
```

Delete container and image:

```bash
inv podman-delete
```

## Invoke Tasks

List tasks:

```bash
inv --list
```

## License

`swift-api-graphql` is distributed under the terms of the [Apache 2.0 ](https://spdx.org/licenses/Apache-2.0.html) license.
