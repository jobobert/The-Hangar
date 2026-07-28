def rendercard():
    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        return render_card_error('Unable to locate the associated model', 'radio_channel', 'Radio Channels')

    ch_query = db(db.radio_channel.model == model_id)

    newform = SQLFORM(db.radio_channel,
                      fields=['channel_num', 'name', 'frequency_mhz', 'duplex', 'offset_mhz',
                              'tone_mode', 'ctcss_freq', 'dtcs_code', 'channel_mode', 'skip', 'channel_comment'],
                      formstyle='divs')
    disable_autocomplete(newform)
    newform.vars.model = model_id
    if newform.process(session=None, formname='newchannel').accepted:
        response.flash = 'Channel added'
    elif newform.errors:
        response.flash = 'Error adding channel'

    deleteform = SQLFORM.factory()
    if deleteform.process(session=None, formname='channeldeleteform').accepted:
        for y, z in request.vars.items():
            if z == 'Remove':
                db(db.radio_channel.id == y).delete()
                response.flash = 'Channel removed'
    elif deleteform.errors:
        response.flash = 'Remove failed'

    channels = ch_query.select(orderby=db.radio_channel.channel_num)
    ch_count  = len(channels)

    return dict(channels=channels, ch_count=ch_count, model_id=model_id,
                newform=newform, deleteform=deleteform)


def update():
    response.title = 'Edit Radio Channel'

    ch_id = VerifyTableID('radio_channel', request.args(0))
    if not ch_id:
        session.flash = 'Invalid channel ID'
        redirect(URL('default', 'index'))

    form = SQLFORM(db.radio_channel, ch_id, showid=False).process()
    if form.accepted:
        model_id = db.radio_channel(form.vars.id).model
        redirect(URL('model', 'index', args=model_id, extension='html'))

    disable_autocomplete(form)
    return dict(form=form)


def delete():
    ch_id = VerifyTableID('radio_channel', request.args(0))
    if ch_id:
        ch = db.radio_channel(ch_id)
        model_id = ch.model if ch else None
        db(db.radio_channel.id == ch_id).delete()
        session.flash = 'Channel deleted'
        redirect(URL('model', 'index', args=model_id, extension='html'))
    else:
        session.flash = 'Invalid channel ID'
        redirect(URL('default', 'index'))


def import_chirp():
    import csv, io

    model_id = VerifyTableID('model', request.args(0))
    if not model_id:
        session.flash = 'Invalid model'
        redirect(URL('default', 'index'))

    def _safe_float(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    if request.vars.csvfile:
        raw    = request.vars.csvfile.file.read().decode('utf-8', errors='replace')
        reader = csv.DictReader(io.StringIO(raw))
        count  = 0
        for row in reader:
            loc = (row.get('Location') or '').strip()
            if not loc.isdigit():
                continue
            freq_str = (row.get('Frequency') or '').strip()
            try:
                freq = float(freq_str)
            except ValueError:
                continue
            db.radio_channel.update_or_insert(
                (db.radio_channel.model    == model_id) &
                (db.radio_channel.channel_num == int(loc)),
                model         = model_id,
                channel_num   = int(loc),
                name          = (row.get('Name') or '').strip()[:8],
                frequency_mhz = freq,
                duplex        = (row.get('Duplex') or '').strip(),
                offset_mhz    = _safe_float(row.get('Offset')),
                tone_mode     = (row.get('Tone') or '').strip(),
                ctcss_freq    = _safe_float(row.get('cToneFreq')),
                dtcs_code     = (row.get('DtcsCode') or '').strip(),
                channel_mode    = (row.get('Mode') or 'FM').strip(),
                skip            = bool((row.get('Skip') or '').strip()),
                channel_comment = (row.get('Comment') or '').strip(),
            )
            count += 1
        session.flash = f'{count} channel(s) imported'
    else:
        session.flash = 'No file received'

    redirect(URL('model', 'index', args=model_id, extension='html'))
