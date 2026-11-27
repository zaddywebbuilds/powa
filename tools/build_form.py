"""Generate the Fluent Forms order form from config.js.

The form supplied with the site (form 42, "Man Powa") collects a name, a
free-text address, a phone number and a package chosen with CHECK BOXES, so a
customer can tick all three and no total is recorded anywhere. It also
redirects to the old domain on submit.

This writes a replacement that matches the order form the static build already
had: state as its own dropdown, one package only, and hidden fields carrying
the reference and the total the customer actually saw. The states, the package
names and the prices are read from assets/js/config.js, so they cannot drift
away from the prices on the page.

    python tools/build_form.py

Import the result under Fluent Forms, All Forms, Import/Export.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'wordpress' / 'knack-extra-order-form.json'

TITLE = 'Knack Extra order'

REQUIRED = {
    'required': {
        'value': True,
        'message': 'This field is required',
        'global_message': 'This field is required',
        'global': True,
    }
}
OPTIONAL = {
    'required': {
        'value': False,
        'message': 'This field is required',
        'global_message': 'This field is required',
        'global': True,
    }
}

_key = [0]


def uniq() -> str:
    _key[0] += 1
    return 'el_%d%03d' % (int(time.time() * 1000), _key[0])


def read_config() -> dict:
    """Evaluate config.js with node and hand back window.KNACK."""
    js = (
        "global.window = {};"
        "require(%s);"
        "process.stdout.write(JSON.stringify(window.KNACK));"
        % json.dumps(str(ROOT / 'assets' / 'js' / 'config.js'))
    )
    out = subprocess.run(
        ['node', '-e', js], capture_output=True, text=True, check=True
    )
    return json.loads(out.stdout)


# ------------------------------------------------------------- field types --

def base(label, name, container='', help_text='', admin=''):
    return {
        'container_class': container,
        'label': label,
        'label_placement': '',
        'admin_field_label': admin or label,
        'help_message': help_text,
        'conditional_logics': [],
    }


def text(label, name, placeholder='', required=True, container='', help_text=''):
    s = base(label, name, container, help_text)
    s.update({
        'prefix_label': '',
        'suffix_label': '',
        'validation_rules': REQUIRED if required else OPTIONAL,
        'is_unique': 'no',
        'unique_validation_message': 'This value need to be unique.',
    })
    return {
        'index': 0,
        'element': 'input_text',
        'attributes': {
            'type': 'text', 'name': name, 'value': '', 'class': '',
            'placeholder': placeholder, 'maxlength': '',
        },
        'settings': s,
        'editor_options': {
            'title': 'Simple Text', 'icon_class': 'ff-edit-text', 'template': 'inputText',
        },
        'uniqElKey': uniq(),
    }


def textarea(label, name, placeholder='', required=True, help_text=''):
    s = base(label, name, '', help_text)
    s.update({
        'validation_rules': REQUIRED if required else OPTIONAL,
        'is_unique': 'no',
        'unique_validation_message': 'This value need to be unique.',
    })
    return {
        'index': 0,
        'element': 'textarea',
        'attributes': {
            'name': name, 'value': '', 'id': '', 'class': '',
            'placeholder': placeholder, 'rows': '3', 'cols': '2', 'maxlength': '',
        },
        'settings': s,
        'editor_options': {
            'title': 'Text Area', 'icon_class': 'ff-edit-textarea', 'template': 'inputTextarea',
        },
        'uniqElKey': uniq(),
    }


def dropdown(label, name, options, placeholder='', required=True, container=''):
    s = base(label, name, container)
    s.update({
        'dynamic_default_value': '',
        'placeholder': placeholder,
        'max_selection': '',
        'advanced_options': options,
        'calc_value_status': False,
        'enable_image_input': False,
        'randomize_options': 'no',
        'validation_rules': REQUIRED if required else OPTIONAL,
        'values_visible': False,
    })
    return {
        'index': 0,
        'element': 'select',
        'attributes': {
            'name': name, 'value': '', 'id': '', 'class': '',
            'placeholder': placeholder, 'multiple': False,
        },
        'settings': s,
        'editor_options': {
            'title': 'Dropdown', 'icon_class': 'ff-edit-dropdown',
            'element': 'select', 'template': 'select',
        },
        'uniqElKey': uniq(),
    }


def radio(label, name, options, container='', help_text=''):
    s = base(label, name, container, help_text)
    s.update({
        'dynamic_default_value': '',
        'display_type': '',
        'advanced_options': options,
        'calc_value_status': False,
        'enable_image_input': False,
        'values_visible': False,
        'randomize_options': 'no',
        'enable_other_option': 'no',
        'validation_rules': REQUIRED,
        'layout_class': '',
    })
    return {
        'index': 0,
        'element': 'input_radio',
        'attributes': {'type': 'radio', 'name': name, 'value': ''},
        'settings': s,
        'editor_options': {
            'title': 'Radio Field', 'icon_class': 'ff-edit-radio', 'template': 'inputRadio',
        },
        'uniqElKey': uniq(),
    }


def checkbox(label, name, option_label, required=True, container=''):
    s = base(label, name, container)
    s.update({
        'dynamic_default_value': '',
        'display_type': '',
        'advanced_options': [
            {'label': option_label, 'value': 'yes', 'calc_value': '', 'image': '', 'id': 0}
        ],
        'calc_value_status': False,
        'enable_image_input': False,
        'values_visible': False,
        'randomize_options': 'no',
        'enable_other_option': 'no',
        'validation_rules': REQUIRED if required else OPTIONAL,
        'layout_class': '',
    })
    return {
        'index': 0,
        'element': 'input_checkbox',
        'attributes': {'type': 'checkbox', 'name': name, 'value': []},
        'settings': s,
        'editor_options': {
            'title': 'Check Box', 'icon_class': 'ff-edit-checkbox-1', 'template': 'inputCheckable',
        },
        'uniqElKey': uniq(),
    }


def hidden(name, admin_label):
    return {
        'index': 0,
        'element': 'input_hidden',
        'attributes': {'type': 'hidden', 'name': name, 'value': ''},
        'settings': {
            'container_class': '',
            'label': '',
            'admin_field_label': admin_label,
            'validation_rules': {},
            'conditional_logics': [],
        },
        'editor_options': {
            'title': 'Hidden Field', 'icon_class': 'ff-edit-hidden-field',
            'template': 'inputHidden',
        },
        'uniqElKey': uniq(),
    }


# -------------------------------------------------------------------- form --

def build(cfg: dict) -> dict:
    states = [
        {'label': s, 'value': s, 'calc_value': '', 'id': i}
        for i, s in enumerate(cfg['order']['states'])
    ]

    sym = cfg['site']['currencySymbol']
    packages = []
    for i, p in enumerate(cfg['packages']):
        unit = round(p['price'] / p['qty'])
        label = '%s - %s%s' % (p['name'], sym, format(p['price'], ','))
        if p['qty'] > 1:
            label += ' (%s%s per bottle)' % (sym, format(unit, ','))
        packages.append(
            # value is the package id, so site.js can match it without having
            # to read a price out of a label.
            {'label': label, 'value': p['id'], 'calc_value': '', 'image': '', 'id': i}
        )

    fields = [
        text('Full name', 'names', 'Your full name'),
        text('Phone number', 'phone', '0803 000 0000', container='ke-half'),
        text('Second number', 'phone_alt', 'Optional', required=False, container='ke-half'),
        dropdown('State', 'state', states, 'Select a state', container='ke-half'),
        text('City or LGA', 'city', '', container='ke-half'),
        textarea('Delivery address', 'address', 'House number, street, area'),
        text('Nearest landmark', 'landmark', 'Optional, it helps the rider', required=False),
        textarea(
            'Delivery instructions', 'notes',
            'Best time to call, gate instructions, anything useful.',
            required=False,
        ),
        radio('Your package', 'package', packages, container='ke-packages',
              help_text='This follows the package you picked above.'),
        checkbox(
            'Confirmation', 'consent',
            'I am 18 or over, and I am happy for my details to be used to confirm and deliver this order.',
        ),
        checkbox(
            'Marketing', 'marketing',
            'Optional: you may message me about offers later. Leave this unticked and we will only contact you about this order.',
            required=False,
        ),
        hidden('order_reference', 'Order reference'),
        hidden('order_package', 'Package'),
        hidden('order_quantity', 'Bottles'),
        hidden('order_subtotal', 'Subtotal'),
        hidden('order_total', 'Total payable'),
    ]

    success = (
        '<p><strong>Thank you. Your order has been received.</strong></p>'
        '<p>Your reference is {inputs.order_reference}. Nothing has been dispatched yet, '
        'and nothing has been charged.</p>'
        '<p>A member of our team will call you on the number you gave, to confirm the address '
        'and agree a delivery window. You pay the rider when the parcel reaches you. We will '
        'never ask you for a card number, a PIN or a one-time code.</p>'
    )

    form_settings = {
        'confirmation': {
            'redirectTo': 'samePage',
            'messageToShow': success,
            'customPage': None,
            'samePageFormBehavior': 'hide_form',
            'customUrl': '',
        },
        'restrictions': {
            'denyEmptySubmission': {
                'enabled': True,
                'message': "Sorry, you cannot submit an empty form.",
            },
        },
        'layout': {
            'labelPlacement': 'top',
            'asteriskPlacement': 'asterisk-right',
            'helpMessagePlacement': 'with_label',
            'errorMessagePlacement': 'inline',
            'cssClassName': '',
        },
        'delete_entry_on_submission': 'no',
    }

    notification = {
        'name': 'New order',
        'sendTo': {'type': 'email', 'email': '{wp.admin_email}'},
        'fromName': '',
        'fromEmail': '',
        'replyTo': '',
        'bcc': '',
        'subject': 'New order {inputs.order_reference} - {inputs.order_package}',
        'message': (
            '<p>A new order was placed on the website.</p>'
            '<p><strong>Reference:</strong> {inputs.order_reference}<br>'
            '<strong>Package:</strong> {inputs.order_package}<br>'
            '<strong>Total payable:</strong> {inputs.order_total}</p>'
            '<p>{all_data}</p>'
        ),
        'conditionals': {'status': False, 'type': 'all', 'conditions': []},
        'enabled': True,
        'email_template': '',
    }

    metas = [
        {'meta_key': 'formSettings', 'value': json.dumps(form_settings)},
        {'meta_key': 'template_name', 'value': 'blank_form'},
        {'meta_key': 'notifications', 'value': json.dumps(notification)},
        {'meta_key': '_primary_email_field', 'value': ''},
    ]

    return {
        'title': TITLE,
        'status': 'published',
        'appearance_settings': None,
        'form_fields': {
            'fields': fields,
            'submitButton': {
                'uniqElKey': uniq(),
                'element': 'button',
                'attributes': {'type': 'submit', 'class': ''},
                'settings': {
                    'align': 'left',
                    'button_style': 'default',
                    'container_class': '',
                    'help_message': '',
                    'button_size': 'lg',
                    'button_ui': {'type': 'default', 'text': 'Confirm my order', 'img_url': ''},
                    # Left blank on purpose. The theme stylesheet colours this
                    # button; inline colours here would fight it.
                    'normal_styles': {},
                    'hover_styles': {},
                    'current_state': 'normal_styles',
                },
                'editor_options': {'title': 'Submit Button'},
            },
        },
        'has_payment': '0',
        'type': 'form',
        'conditions': None,
        'form_meta': metas,
        'metas': metas,
    }


def main() -> None:
    cfg = read_config()
    form = build(cfg)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps([form], indent=1), encoding='utf-8')

    n_fields = len(form['form_fields']['fields'])
    print('form    : %s' % OUT)
    print('fields  : %d  (%d states, %d packages)'
          % (n_fields, len(cfg['order']['states']), len(cfg['packages'])))
    print('import  : Fluent Forms, All Forms, Import/Export, Import Forms')


if __name__ == '__main__':
    main()
