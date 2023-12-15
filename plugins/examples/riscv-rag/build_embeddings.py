import os, sys, subprocess

# Add the root of the repo to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def press_key_to_continue(text: str):
   input(f'{text}. Press enter to continue...')

cwd = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'data')
splitter_py = ['python', os.path.join(cwd, 'splitter.py')]
count_tokens_py = ['python', os.path.join(cwd, 'count_tokens.py')]
gentoc_py = ['python', os.path.join(cwd, 'gentoc.py')]
combiner_py = ['python', os.path.join(cwd, 'combiner.py')]

def main():
   subprocess.call(splitter_py, cwd=cwd)
   press_key_to_continue('Finished splitting')
   subprocess.call(count_tokens_py, cwd=cwd)
   press_key_to_continue(
      'Please verify the token counts in output_tokens.json')
   subprocess.call(gentoc_py, cwd=cwd)
   press_key_to_continue('Please verify the table of contents')
   subprocess.call(combiner_py, cwd=cwd)
   press_key_to_continue(
      'Please verify the combined output in output_tokens_combined.json')
   # Now we can import and use the schema
   from data.schema import build_embeddings
   build_embeddings()

if __name__ == '__main__':
   main()
