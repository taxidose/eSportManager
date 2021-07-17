from website import create_app
import logging


app = create_app()



def main():
    logging.basicConfig(format="[%(levelname)s %(asctime)s] %(message)s", filename="info.log", level=logging.INFO)
    logging.info('Started')
    app.run(debug=True)

    logging.info('Finished')


if __name__ == '__main__':
    main()