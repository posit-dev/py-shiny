export class ImmutableSet<T> {
  private _set: Set<T>;
  private static _empty: ImmutableSet<unknown> = new ImmutableSet(new Set());

  private constructor(set: Set<T>) {
    this._set = set;
  }

  static empty<T>(): ImmutableSet<T> {
    return this._empty as ImmutableSet<T>;
  }

  static just<T>(...values: T[]): ImmutableSet<T> {
    return this.empty<T>().add(...values);
  }

  has(value: T): boolean {
    return this._set.has(value);
  }

  add(...values: T[]): ImmutableSet<T> {
    const newSet = new Set(this._set.keys());
    for (const value of values) {
      newSet.add(value);
    }
    return new ImmutableSet(newSet);
  }

  toggle(value: T): ImmutableSet<T> {
    if (this.has(value)) {
      return this.delete(value);
    } else {
      return this.add(value);
    }
  }

  delete(value: T): ImmutableSet<T> {
    const newSet = new Set(this._set.keys());
    newSet.delete(value);
    return new ImmutableSet(newSet);
  }

  clear(): ImmutableSet<T> {
    return ImmutableSet.empty();
  }

  [Symbol.iterator]() {
    return this._set[Symbol.iterator]();
  }

  toList(): T[] {
    return [...this._set.keys()];
  }
}
