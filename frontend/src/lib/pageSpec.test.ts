import { describe, it, expect } from 'vitest'
import { normalizePageSpec } from './pageSpec'

describe('normalizePageSpec', () => {
  it('should return empty string for empty or whitespace-only inputs', () => {
    expect(normalizePageSpec('')).toBe('')
    expect(normalizePageSpec('   ')).toBe('')
    expect(normalizePageSpec('\t\n')).toBe('')
  })

  it('should handle "ALL" keyword case-insensitively and trim spaces', () => {
    expect(normalizePageSpec('ALL')).toBe('ALL')
    expect(normalizePageSpec('all')).toBe('ALL')
    expect(normalizePageSpec(' aLl ')).toBe('ALL')
  })

  it('should handle "LAST" keyword case-insensitively and trim spaces', () => {
    expect(normalizePageSpec('LAST')).toBe('LAST')
    expect(normalizePageSpec('last')).toBe('LAST')
    expect(normalizePageSpec(' lAsT ')).toBe('LAST')
  })

  it('should remove all whitespaces from a standard page spec string', () => {
    expect(normalizePageSpec('1, 2, 3')).toBe('1,2,3')
    expect(normalizePageSpec(' 1,2 , 3-5 ')).toBe('1,2,3-5')
    expect(normalizePageSpec('1,   4\t,\n5-7')).toBe('1,4,5-7')
  })
})
