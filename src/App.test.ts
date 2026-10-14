import { describe, expect, it } from 'vitest'
import { naira } from './App'

describe('CampusCircle financial display helpers', () => {
  it('formats balances as Nigerian naira without decimal drift', () => {
    expect(naira(278000)).toBe('₦278,000')
    expect(naira(0)).toBe('₦0')
  })
})
