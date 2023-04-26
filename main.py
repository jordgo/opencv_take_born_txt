import logging.config

import click as click
import yaml
import repositories.db_selector as db_selector
from repositories.db_selector import Databases
import repositories.img_texts_repository as img_texts_repository


from conf.logging_conf import LOGGING_CONFIG
import video_processing.video_handler as video_handler

logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")

with open("./conf/config.yml", 'r') as file:
    config = yaml.safe_load(file)

START_AT = "00:13:02.920000"
# START_AT = "00:13:03.60000"
END_AT = "00:14:03.920000"
# START_AT = "00:00:00.920000"
# END_AT = "00:00:01.920000"


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path(exists=True))
def main(file_path: str, output_folder):
    db, db_obj = db_selector.get_db(Databases.MONGO, config)
    if db_obj.check_connection():
        img_txt_repo = img_texts_repository.ImgTextsRepository(db, config)
        vh = video_handler.VideoHandler(file_path, output_folder, config, img_txt_repo)
        vh.start(start_at_debug=START_AT, end_at_debug=END_AT)
        db_obj.db_close()


if __name__ == "__main__":
    main()
