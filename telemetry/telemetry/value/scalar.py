# Copyright 2013 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import numbers

from telemetry import value as value_module
from telemetry.value import list_of_scalar_values
from telemetry.value import none_values
from telemetry.value import summarizable


class ScalarValue(summarizable.SummarizableValue):
  def __init__(self, page, name, units, value, important=True,
               description=None, tir_label=None,
               none_value_reason=None, improvement_direction=None,
               grouping_keys=None):
    """A single value (float or integer) result from a test.

    A test that counts the number of DOM elements in a page might produce a
    scalar value:
       ScalarValue(page, 'num_dom_elements', 'count', num_elements)
    """
    super(ScalarValue, self).__init__(page, name, units, important, description,
                                      tir_label, improvement_direction,
                                      grouping_keys)
    assert value is None or isinstance(value, numbers.Number)
    none_values.ValidateNoneValueReason(value, none_value_reason)
    self.value = value
    self.none_value_reason = none_value_reason

  def __repr__(self):
    if self.page:
      page_name = self.page.name
    else:
      page_name = 'None'
    return ('ScalarValue(%s, %s, %s, %s, important=%s, description=%s, '
            'tir_label=%s, improvement_direction=%s, grouping_keys=%s') % (
                page_name,
                self.name,
                self.units,
                self.value,
                self.important,
                self.description,
                self.tir_label,
                self.improvement_direction,
                self.grouping_keys)

  @staticmethod
  def GetJSONTypeName():
    return 'scalar'

  def AsDict(self):
    d = super(ScalarValue, self).AsDict()
    d['value'] = self.value

    if self.none_value_reason is not None:
      d['none_value_reason'] = self.none_value_reason

    return d

  @classmethod
  def MergeLikeValuesFromSamePage(cls, values):
    assert len(values) > 0
    v0 = values[0]
    return cls._MergeLikeValues(values, v0.page, v0.name, v0.grouping_keys)

  @classmethod
  def MergeLikeValuesFromDifferentPages(cls, values):
    assert len(values) > 0
    v0 = values[0]
    return cls._MergeLikeValues(values, None, v0.name, v0.grouping_keys)

  @classmethod
  def _MergeLikeValues(cls, values, page, name, grouping_keys):
    v0 = values[0]

    merged_value = [v.value for v in values]
    none_value_reason = None
    if None in merged_value:
      merged_value = None
      merged_none_values = [v for v in values if v.value is None]
      none_value_reason = (
          none_values.MERGE_FAILURE_REASON +
          ' None values: %s' % repr(merged_none_values))
    return list_of_scalar_values.ListOfScalarValues(
        page, name, v0.units, merged_value, important=v0.important,
        description=v0.description,
        tir_label=value_module.MergedTirLabel(values),
        none_value_reason=none_value_reason,
        improvement_direction=v0.improvement_direction,
        grouping_keys=grouping_keys)
