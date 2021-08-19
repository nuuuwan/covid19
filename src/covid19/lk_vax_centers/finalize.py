def finalize(date_id):
    date_id = timex.get_date_id()
    for ext in ['pdf', 'tsv', 'si.md', 'en.md', 'ta.md']:
        old_file = get_file('latest', ext)
        new_file = get_file(date_id, ext)
        os.system('cp "%s" "%s"' % (old_file, new_file))
        log.info(f'Copied {old_file} to {new_file}')
