from flask import redirect, url_for


def handle_legacy_redirect(args, target):
    service = args.get('service')
    if service == 'youtube':
        redirect_args = {
            **args,
            'service': 'youtube.com'
        }
    elif service == 'invidious':
        redirect_args = {
            **args,
            'plugin': 'invidious'
        }
        del redirect_args['service']
    elif service and '.' not in service:
        redirect_args = {
            **args,
            'plugin': service
        }
        del redirect_args['service']
    else:
        return None

    return redirect(url_for(target, **redirect_args), code=301)
