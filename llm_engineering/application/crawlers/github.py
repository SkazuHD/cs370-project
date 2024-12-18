import os
import pathlib
import shutil
import subprocess
import tempfile

from loguru import logger

from llm_engineering.domain.documents import RepositoryDocument

from .base import BaseCrawler


class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__(
        self,
        include=(
            ".txt",
            ".md",
            ".rst",
            ".json",
            ".yml",
            ".yaml",
            ".xml",
            ".html",
            ".csv",
            ".py",
            ".sh",
            ".cfg",
            ".conf",
            ".js",
            ".css",
            ".scss",
            ".cpp",
            ".hpp",
            ".h",
            ".cc",
            ".hh",
            ".cmake",
            ".bat",
            ".rb",
            ".bash",
            ".qml",
            ".proto",
            ".properties",
            ".template",
            ".in",
            ".inc",
            ".pyi",
            ".typed",
        ),
        ignore=(
            ".git",
            ".toml",
            ".lock",
            ".png",
            ".gitignore",
            ".ico",
            ".jpg",
            ".jpeg",
            ".webp",
            ".svg",
            ".gif",
            ".stl",
            ".dae",
            ".jar",
            ".pdf",
        ),
    ) -> None:
        super().__init__()
        self._ignore = ignore
        self._include = include

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")

            return

        logger.info(f"Starting scrapping GitHub repository: {link}")

        repo_name = link.rstrip("/").split("/")[-1]

        local_temp = tempfile.mkdtemp()
        file_types = {}
        try:
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link], check=True)

            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])  # noqa: PTH118

            tree = {}
            current_size = 0
            max_size = 16793598 - 100000  # 16 MB in bytes

            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(tuple(self._ignore)):
                    continue
                for file in files:
                    if file.endswith(tuple(self._ignore)) or file.startswith("."):
                        continue
                    if not file.endswith(tuple(self._include)):
                        continue
                    file_path = os.path.join(dir, file)  # noqa: PTH118
                    full_file_path = os.path.join(root, file)  # noqa: PTH118

                    try:
                        with open(full_file_path, "r", errors="ignore") as f:  # noqa: PTH123
                            file_extension = pathlib.Path(full_file_path).suffix
                            file_types[file_extension] = 1
                            content = f.read().replace(" ", "")
                        file_size = len(content.encode("utf-8"))

                        # Check if adding this file exceeds the size limit
                        if current_size + file_size > max_size:
                            # Save the current tree and clear it
                            self.save_tree(tree, repo_name, link)
                            tree.clear()
                            current_size = 0

                        # Add file to tree
                        tree[file_path] = content
                        current_size += file_size

                    except Exception as e:
                        logger.error(f"Failed to process file {file_path}: {e}")

            # Save any remaining files in the tree
            if tree:
                self.save_tree(tree, repo_name, link)

        except Exception as e:
            logger.error(f"Error while processing repository: {e}")
            raise
        finally:
            shutil.rmtree(local_temp, ignore_errors=True)

        logger.info(f"Finished scrapping GitHub repository: {link}")
        logger.info(file_types)

    def save_tree(self, tree, repo_name, link):
        """Helper method to save the current tree."""
        try:
            instance = self.model(
                content=tree,
                name=repo_name,
                link=link,
                platform="github",
                author_id="46648381-8bf3-4877-b6b4-d48c9de9d870",
                author_full_name="CS370 Project",
            )
            instance.save()
        except Exception as e:
            logger.error(f"Failed to save tree: {e}")
