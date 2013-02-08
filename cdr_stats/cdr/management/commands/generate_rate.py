# -*- coding: utf-8 -*-

#
# CDR-Stats License
# http://www.cdr-stats.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2012 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#
from django.conf import settings
from django.core.management.base import BaseCommand
from voip_billing.models import VoIPRetailRate, VoIPPlan, BanPlan,\
    VoIPPlan_BanPlan, BanPrefix, VoIPRetailPlan, VoIPPlan_VoIPRetailPlan,\
    VoIPCarrierPlan, VoIPCarrierRate, VoIPPlan_VoIPCarrierPlan
from country_dialcode.models import Prefix
from optparse import make_option
from random import choice
import random


random.seed()


class Command(BaseCommand):
    args = ' number-rate, call-plan '
    help = "Generate random rates\n"\
           "---------------------------------\n"\
           "python manage.py generate_rate --number-rate=100 --call-plan=1"

    option_list = BaseCommand.option_list + (
        make_option('--number-rate',
                    default=None,
                    dest='number-rate',
                    help=help),
        make_option('--call-plan',
                    default=1,
                    dest='call-plan',
                    help=help),
    )

    def handle(self, *args, **options):
        """
        Note that rates created this way are only for devel purposes
        """
        no_of_record = 1  # default
        if options.get('number-rate'):
            try:
                no_of_record = int(options.get('number-rate'))
            except ValueError:
                no_of_record = 1

        call_plan = 1  # default
        if options.get('call-plan'):
            try:
                call_plan = int(options.get('call-plan'))
                voip_plan_id = VoIPPlan.objects.get(pk=int(call_plan))
            except ValueError:
                voip_plan_id = 1


        for i in range(1, int(no_of_record) + 1):
            carrierplanid = VoIPPlan_VoIPCarrierPlan.objects.get(voipplan=voip_plan_id).voipcarrierplan_id
            carrier_plan = VoIPCarrierPlan.objects.get(pk=carrierplanid)

            retail_plan = VoIPRetailPlan.objects.get(voip_plan=voip_plan_id)

            # get random prefixes from Prefix
            prefix = Prefix.objects.order_by('?')[0]

            # Create carrier_rate & retail_rate with random prefix
            carrier_rate = '%.4f' % random.random()

            # No duplication
            if VoIPCarrierRate.objects.filter(prefix=prefix).count() == 0:
                VoIPCarrierRate.objects.create(
                    voip_carrier_plan_id=carrier_plan,
                    prefix=prefix,
                    carrier_rate=float(carrier_rate)
                )

            # retail_rate = 10% increase in carrier_rate
            retail_rate = float(carrier_rate) + ((float(carrier_rate) * 10)/100)

            # No duplication
            if VoIPRetailRate.objects.filter(prefix=prefix).count() == 0:
                VoIPRetailRate.objects.create(
                    voip_retail_plan_id=retail_plan,
                    prefix=prefix,
                    retail_rate=float(retail_rate)
                )
