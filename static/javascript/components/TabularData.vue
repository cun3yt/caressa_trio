<template>
    <div>
        <form v-on:submit.prevent="onSubmit()">
            <table>
                <thead>
                <tr>
                    <th v-for="col_obj in columns" @click="sortBy(col_obj)"
                        :class="{ active: sortKey == col_obj.field }">
                        {{ col_obj.label }}
                        <span v-if="col_obj.sortable"
                              class="arrow" :class="sortOrders[col_obj.field] > 0 ? 'asc' : 'dsc'"></span>
                    </th>
                    <th>Edit</th>
                </tr>
                </thead>

                <tbody>
                <tr v-for="entry in filteredData">
                    <td v-for="(col_obj, key) in columns">
                        <grid-unit :content="entry[col_obj.field]" :is-edit="false"
                                   :name="col_obj.field"></grid-unit>
                    </td>
                    <td>
                        <i class="far fa-edit" v-on:click="editEntry(entry)"
                           style="font-size:26px; color:seagreen; cursor: pointer;"></i>
                        <i class="fas fa-ban" v-on:click="deleteEntry(entry.pk)"
                           style="font-size:26px; color:indianred; cursor: pointer;"></i>
                    </td>
                </tr>
                <tr v-if="filterKey && filteredData.length==0">
                    <td :colspan="columns.length+1" style="color:indianred;">No entry found for search
                        "{{ filterKey }}"
                    </td>
                </tr>

                <tr>
                    <td v-for="(col_obj, key) in columns" style="border-top: darkblue solid 1px;">
                        <label v-bind:for="col_obj.field" style="font-weight: bold;">{{ col_obj.label }}</label><br>
                        <grid-unit
                                v-if="col_obj.field=='primary_contact'"
                                :content="[{'key': 'contact.name', 'label': 'Name', 'value': ''},
                                          {'key': 'contact.email', 'label': 'Email', 'value': ''},
                                          {'key': 'contact.phone_number', 'label': 'Phone Number', 'value': ''}]"
                                :is-edit="true"
                                :name="col_obj.field"
                                :id="col_obj.field"></grid-unit>
                        <grid-unit v-else :content="['']" :is-edit="true" :name="col_obj.field"
                                   :id="col_obj.field"></grid-unit>
                    </td>
                    <td style="border-top: darkblue solid 1px;">
                        <button type="submit"><i class="fas fa-plus" style="font-size:26px"></i> Add</button>
                    </td>
                </tr>
                </tbody>
            </table>
        </form>
    </div>
</template>

<script>
    import GridUnit from '../components/GridUnit.vue'

    export default {
        name: "TabularData",
        components: {GridUnit},
        props: {
            data: Array,
            columns: Array,
            filterKey: String,
            editEntry: Function,
            deleteEntry: Function,
            onSubmit: Function
        },
        data: function () {
            let sortOrders = {}
            this.columns.forEach(function (key) {
                sortOrders[key.field] = 1
            })
            return {
                sortKey: '',
                sortOrders: sortOrders
            }
        },
        computed: {
            filteredData: function () {
                let sortKey = this.sortKey
                let filterKey = this.filterKey && this.filterKey.toLowerCase()
                let order = this.sortOrders[sortKey] || 1
                let data = this.data
                if (filterKey) {
                    data = data.filter(function (row) {
                        return Object.keys(row).some(function (key) {
                            return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                        })
                    })
                }
                if (sortKey) {
                    data = data.slice().sort(function (a, b) {
                        a = a[sortKey][0].toLowerCase()
                        b = b[sortKey][0].toLowerCase()
                        return (a === b ? 0 : a > b ? 1 : -1) * order
                    })
                }
                return data
            }
        },
        methods: {
            sortBy: function (col_obj) {
                if( ! col_obj.sortable ) {
                    return
                }
                let key = col_obj.field
                this.sortKey = key
                this.sortOrders[key] = this.sortOrders[key] * -1
            }
        }
    }
</script>

<style scoped>
    table {
        border: 2px solid #42b983;
        border-radius: 3px;
        background-color: #fff;
    }

    th {
        background-color: #42b983;
        color: rgba(255, 255, 255, 0.66);
        cursor: pointer;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    td {
        background-color: #f9f9f9;
    }

    th, td {
        min-width: 120px;
        padding: 10px 20px;
    }

    th.active {
        color: #fff;
    }

    th.active .arrow {
        opacity: 1;
    }

    .arrow {
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin-left: 5px;
        opacity: 0.66;
    }

    .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid #fff;
    }

    .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #fff;
    }
</style>
