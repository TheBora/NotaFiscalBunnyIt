import os
import datetime
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


def link_callback(uri, rel):
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
        return path

def get_nota_fiscal(request):
    template_path = 'comprovante.html'
    now = datetime.datetime.now()
    context = {
        'cart': [
            {
                'id': 1,
                'description': 'Post it',
                'price': 8.9,
                'quantity': 5,
                'subtotal': 44.5
            },
            {
                'id': 2,
                'description': 'Caneta em gel',
                'price': 4.9,
                'quantity': 2,
                'subtotal': 9.8
            },
            {
                'id': 3,
                'description': 'Canetão de lousa branca',
                'price': 13.9,
                'quantity': 4,
                'subtotal': 55.6
            },
            {
                'id': 4,
                'description': 'Apagador',
                'price': 9.9,
                'quantity': 1,
                'subtotal': 9.9
            }
        ],
        'totalPrice': 119.8,
        'dateTime': datetime.datetime.strftime(now, ' %d/%m/%Y %H:%M:%S')
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="NotaFiscalBunnyIt.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response