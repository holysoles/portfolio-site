# portfolio-site
Website to highlight personal projects, written in Python, built on Flask and Jinja templating.

## YAML-based posts

Individual project posts to the home page are defined via yaml files, with support for proper HTML tags (headings and subheadings, paragraph text, divs, and more) in addition to inline code snippets and images.

I chose this approach as an introduction to working with Flask and to leverage Jinja templates in a way I haven't seen before. This project design allows to me to maintain the site without needing a more complex solution for blog post entries, such as a database.

## Docker
### Image
A docker image that runs this application is available under the repo packages, or at `ghcr.io/holysoles/portfolio-site`.
### Compose
An example compose file can be found in the repo [here](https://github.com/holysoles/portfolio-site/blob/master/compose.yaml)
### Building
`docker build --tag ghcr.io/holysoles/portfolio-site:<tag> .`
### Testing
`docker run --rm -d -p 5000:5000 ghcr.io/holysoles/portfolio-site:<tag>`
### Upload
`docker push ghcr.io/holysoles/portfolio-site:<tag>`