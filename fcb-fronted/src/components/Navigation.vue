<template>
    <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      @select="handleSelect"
    >
      <el-menu-item index="1">文件快递</el-menu-item>
      <el-menu-item index="2">博客</el-menu-item>
    </el-menu>
  </template>
  
<script lang="ts" setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router';

  const router = useRouter()
  const activeIndex = ref('1')
  const handleSelect = (key: string, keyPath: string[]) => {
    if (key === '1') {
        router.push('/')
    } else if (key === '2') {
        window.open('https://me.liuyaowen.club/')
    }
  }
</script>
  