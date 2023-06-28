import argparse
import logging
import pathlib

import app
from models import Registry


def _serve_command_handler(args) -> None:
    registry = Registry.from_binary_file(args.datafile)
    app.run(registry, args.host, args.port)

def _index_command_handler(args) -> None:
    registry = Registry.from_binary_file()
    registry.add_documents_from_directory(args.directory)
    registry.dump_to_binary_file()

def _info_command_handler(args) -> None:
    assert args.datafile.exists(), "Registry data file does not exist."

    registry = Registry.from_binary_file(args.datafile)

    print(f'----- REGISTRY INFO: "{args.datafile}" -----')
    print(f'docs count: {len(registry.docs)}')
    print(f'registry file size: {(args.datafile.stat().st_size / 1024):.3f}KB')

parser = argparse.ArgumentParser(
    prog='docserve',
    description='Offline documentation provider, capable of parsing XML, HTML, TXT and PDF documentation files')
subparsers = parser.add_subparsers(required=True)

serve_command_parser = subparsers.add_parser(
    'serve',
    help='Starts documentation server at given host and port.')
serve_command_parser.set_defaults(command_handler=_serve_command_handler)
serve_command_parser.add_argument(
    '-H', '--host',
    type=str,
    required=False,
    default=app.DEFAULT_HOST,
    help='Host on which docserve will run')
serve_command_parser.add_argument(
    '-P', '--port',
    type=int,
    required=False,
    default=app.DEFAULT_PORT,
    help='Port on which docserve will run')
serve_command_parser.add_argument(
    '-d', '--datafile',
    type=pathlib.Path,
    required=False,
    default=Registry.DEFAULT_REGISTRY_DATA_FILEPATH,
    help='Filepath pointing to the binary data file that will be used to initialize docs registry.')

index_command_parser = subparsers.add_parser(
    'index',
    help='Indexes all documentation files from given directory and adds them to docs registry.')
index_command_parser.set_defaults(command_handler=_index_command_handler)
index_command_parser.add_argument(
    'directory',
    type=pathlib.Path,
    help='Directory containing documentation files')

debug_command_parser = subparsers.add_parser('info')
debug_command_parser.set_defaults(command_handler=_info_command_handler)
debug_command_parser.add_argument(
    'datafile',
    type=pathlib.Path,
    help='Registry file which informations should be displayed.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    args = parser.parse_args()
    args.command_handler(args)
